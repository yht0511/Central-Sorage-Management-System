package handlers

import (
	"central-storage-system/database"
	"central-storage-system/models"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// GetItems 获取所有物品（支持分页和搜索）
func GetItems(c *gin.Context) {
	var req models.PaginationRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid query parameters: " + err.Error()})
		return
	}
	req.SetDefaults()

	var items []models.Item
	var total int64
	
	// 构建查询
	query := database.DB.Preload("Section.Storage.Laboratory")
	
	// 搜索功能
	if req.Search != "" {
		searchTerm := "%" + req.Search + "%"
		query = query.Where("name LIKE ? OR code LIKE ? OR description LIKE ? OR category LIKE ?", 
			searchTerm, searchTerm, searchTerm, searchTerm)
	}
	
	// 支持按分区ID过滤
	if sectionID := c.Query("section_id"); sectionID != "" {
		query = query.Where("section_id = ?", sectionID)
	}
	
	// 支持按类别过滤
	if category := c.Query("category"); category != "" {
		query = query.Where("category = ?", category)
	}
	
	// 支持低库存警告
	if lowStock := c.Query("low_stock"); lowStock == "true" {
		query = query.Where("quantity <= min_quantity")
	}
	
	// 支持即将过期筛选
	if expiring := c.Query("expiring"); expiring == "true" {
		days := 30
		if daysStr := c.Query("expiring_days"); daysStr != "" {
			if d, err := strconv.Atoi(daysStr); err == nil && d > 0 {
				days = d
			}
		}
		futureDate := time.Now().AddDate(0, 0, days)
		query = query.Where("expiry_date IS NOT NULL AND expiry_date <= ?", futureDate)
	}
	
	// 获取总数
	if err := query.Model(&models.Item{}).Count(&total).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count items"})
		return
	}
	
	// 排序
	orderBy := "created_at DESC" // 默认排序
	if req.SortBy != "" {
		allowedSorts := map[string]bool{
			"name": true, "code": true, "category": true, "quantity": true, 
			"price": true, "created_at": true, "updated_at": true,
		}
		if allowedSorts[req.SortBy] {
			if req.SortDesc {
				orderBy = req.SortBy + " DESC"
			} else {
				orderBy = req.SortBy + " ASC"
			}
		}
	}
	
	// 分页查询
	if err := query.Order(orderBy).Limit(req.PageSize).Offset(req.GetOffset()).Find(&items).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get items"})
		return
	}
	
	// 为每个物品添加位置路径信息
	itemsWithPath := make([]gin.H, len(items))
	for i, item := range items {
		var locationPath models.LocationPath
		
		// 检查关联数据是否存在
		if item.Section.ID != 0 && item.Section.Storage.ID != 0 {
			if item.Section.Storage.Laboratory.ID != 0 {
				locationPath = models.LocationPath{
					LabCode:     item.Section.Storage.Laboratory.Code,
					LabName:     item.Section.Storage.Laboratory.Name,
					StorageCode: item.Section.Storage.Code,
					StorageName: item.Section.Storage.Name,
					SectionCode: item.Section.Code,
					SectionName: item.Section.Name,
					FullPath:    fmt.Sprintf("%s > %s > %s", 
						item.Section.Storage.Laboratory.Name,
						item.Section.Storage.Name,
						item.Section.Name),
				}
			}
		}
		
		itemsWithPath[i] = gin.H{
			"item":     item,
			"section":  item.Section,
			"location": locationPath,
		}
	}
	
	// 创建分页响应
	response := models.CreatePaginationResponse(itemsWithPath, total, &req)
	c.JSON(http.StatusOK, response)
}

// GetItem 获取单个物品详情
func GetItem(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid item ID"})
		return
	}
	
	var item models.Item
	if err := database.DB.Preload("Section.Storage.Laboratory").First(&item, uint(id)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Item not found"})
		return
	}
	
	var locationPath models.LocationPath
	
	// 检查关联数据是否存在
	if item.Section.ID > 0 {
		locationPath.SectionCode = item.Section.Code
		locationPath.SectionName = item.Section.Name
		
		if item.Section.Storage.ID > 0 {
			locationPath.StorageCode = item.Section.Storage.Code
			locationPath.StorageName = item.Section.Storage.Name
			
			if item.Section.Storage.Laboratory.ID > 0 {
				locationPath.LabCode = item.Section.Storage.Laboratory.Code
				locationPath.LabName = item.Section.Storage.Laboratory.Name
				locationPath.FullPath = item.Section.Storage.Laboratory.Name + " → " + item.Section.Storage.Name + " → " + item.Section.Name
			} else {
				locationPath.FullPath = "未知实验室 → " + item.Section.Storage.Name + " → " + item.Section.Name
			}
		} else {
			locationPath.FullPath = "未知位置 → " + item.Section.Name
		}
	} else {
		locationPath.FullPath = "未设置位置"
	}
	
	c.JSON(http.StatusOK, gin.H{
		"item":     item,
		"section":  item.Section,
		"location": locationPath,
	})
}

// CreateItem 创建物品
func CreateItem(c *gin.Context) {
	var item models.Item
	if err := c.ShouldBindJSON(&item); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// 验证分区是否存在
	var section models.Section
	if err := database.DB.First(&section, item.SectionID).Error; err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Section not found"})
		return
	}
	
	if err := database.DB.Create(&item).Error; err != nil {
		// 检查是否是唯一约束错误
		if strings.Contains(err.Error(), "UNIQUE constraint failed: items.code") {
			c.JSON(http.StatusBadRequest, gin.H{"error": "物品编号已存在，请使用不同的编号"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create item"})
		return
	}
	
	// 记录物品移动记录（入库）
	userID, _ := c.Get("user_id")
	movement := models.Movement{
		ItemID:       item.ID,
		MovementType: "入库",
		FromLocation: "",
		ToLocation:   fmt.Sprintf("分区ID:%d", item.SectionID),
		Quantity:     item.Quantity,
		Reason:       "新增物品",
		Notes:        "Initial stock",
		UserID:       userID.(uint),
	}
	database.DB.Create(&movement)
	
	// 重新查询以获取关联数据
	database.DB.Preload("Section.Storage.Laboratory").First(&item, item.ID)
	
	c.JSON(http.StatusCreated, gin.H{"item": item})
}

// UpdateItem 更新物品
func UpdateItem(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid item ID"})
		return
	}
	
	var item models.Item
	if err := database.DB.First(&item, uint(id)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Item not found"})
		return
	}
	
	oldSectionID := item.SectionID
	oldQuantity := item.Quantity
	
	// 创建更新数据结构
	var updateData struct {
		Code         string                 `json:"code"`
		Name         string                 `json:"name"`
		Description  string                 `json:"description"`
		Category     string                 `json:"category"`
		Properties   map[string]interface{} `json:"properties"`
		Price        float64                `json:"price"`
		Quantity     int                    `json:"quantity"`
		MinQuantity  int                    `json:"min_quantity"`
		Unit         string                 `json:"unit"`
		Supplier     string                 `json:"supplier"`
		PurchaseDate *models.CustomDate     `json:"purchase_date"`
		ExpiryDate   *models.CustomDate     `json:"expiry_date"`
		SectionID    uint                   `json:"section_id"`
	}
	
	if err := c.ShouldBindJSON(&updateData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// 如果修改了分区ID，验证新分区是否存在
	if updateData.SectionID != 0 {
		var section models.Section
		if err := database.DB.First(&section, updateData.SectionID).Error; err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Section not found"})
			return
		}
	}
	
	// 更新物品数据
	item.Code = updateData.Code
	item.Name = updateData.Name
	item.Description = updateData.Description
	item.Category = updateData.Category
	item.Properties = updateData.Properties // 确保Properties被正确更新
	item.Price = updateData.Price
	item.Quantity = updateData.Quantity
	item.MinQuantity = updateData.MinQuantity
	item.Unit = updateData.Unit
	item.Supplier = updateData.Supplier
	item.PurchaseDate = updateData.PurchaseDate
	item.ExpiryDate = updateData.ExpiryDate
	item.SectionID = updateData.SectionID
	
	if err := database.DB.Save(&item).Error; err != nil {
		// 检查是否是唯一约束错误
		if strings.Contains(err.Error(), "UNIQUE constraint failed: items.code") {
			c.JSON(http.StatusBadRequest, gin.H{"error": "物品编号已存在，请使用不同的编号"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update item"})
		return
	}
	
	// 记录物品移动记录
	userID, _ := c.Get("user_id")
	
	// 如果位置发生变化，记录转移记录
	if oldSectionID != item.SectionID {
		movement := models.Movement{
			ItemID:       item.ID,
			MovementType: "转移",
			FromLocation: fmt.Sprintf("分区ID:%d", oldSectionID),
			ToLocation:   fmt.Sprintf("分区ID:%d", item.SectionID),
			Quantity:     item.Quantity,
			Reason:       "物品位置更新",
			Notes:        "Item location updated",
			UserID:       userID.(uint),
		}
		database.DB.Create(&movement)
	}
	
	// 如果数量发生变化，记录库存变化
	if oldQuantity != item.Quantity {
		movementType := "入库"
		quantity := item.Quantity - oldQuantity
		reason := "库存增加"
		if quantity < 0 {
			movementType = "出库"
			quantity = -quantity
			reason = "库存减少"
		}
		
		movement := models.Movement{
			ItemID:       item.ID,
			MovementType: movementType,
			FromLocation: fmt.Sprintf("分区ID:%d", item.SectionID),
			ToLocation:   fmt.Sprintf("分区ID:%d", item.SectionID),
			Quantity:     quantity,
			Reason:       reason,
			Notes:        "Quantity updated",
			UserID:       userID.(uint),
		}
		database.DB.Create(&movement)
	}
	
	// 重新查询以获取关联数据
	database.DB.Preload("Section.Storage.Laboratory").First(&item, item.ID)
	
	c.JSON(http.StatusOK, gin.H{"item": item})
}

// DeleteItem 删除物品
func DeleteItem(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid item ID"})
		return
	}
	
	var item models.Item
	if err := database.DB.First(&item, uint(id)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Item not found"})
		return
	}
	
	// 记录物品移动记录（出库）
	userID, _ := c.Get("user_id")
	movement := models.Movement{
		ItemID:       item.ID,
		MovementType: "出库",
		FromLocation: fmt.Sprintf("分区ID:%d", item.SectionID),
		ToLocation:   "",
		Quantity:     item.Quantity,
		Reason:       "物品删除",
		Notes:        "Item deleted",
		UserID:       userID.(uint),
	}
	database.DB.Create(&movement)
	
	if err := database.DB.Delete(&item).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete item"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"message": "Item deleted successfully"})
}

// CheckItemCodeExists 检查物品编号是否存在
func CheckItemCodeExists(c *gin.Context) {
	code := c.Query("code")
	if code == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Code parameter is required"})
		return
	}

	var count int64
	database.DB.Model(&models.Item{}).Where("code = ?", code).Count(&count)
	
	c.JSON(http.StatusOK, gin.H{"exists": count > 0})
}

// GetCategories 获取所有物品类别
func GetCategories(c *gin.Context) {
	var categories []string
	if err := database.DB.Model(&models.Item{}).Distinct("category").Where("category != ''").Pluck("category", &categories).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get categories"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"categories": categories})
}

// GetLowStockItems 获取低库存物品
func GetLowStockItems(c *gin.Context) {
	var items []models.Item
	if err := database.DB.Where("quantity <= min_quantity").Preload("Section.Storage.Laboratory").Find(&items).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get low stock items"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"items": items})
}

// GetExpiringItems 获取即将过期的物品
func GetExpiringItems(c *gin.Context) {
	daysStr := c.DefaultQuery("days", "30")
	days, _ := strconv.Atoi(daysStr)
	
	futureDate := time.Now().AddDate(0, 0, days)
	
	var items []models.Item
	if err := database.DB.Where("expiry_date IS NOT NULL AND expiry_date <= ?", futureDate).Preload("Section.Storage.Laboratory").Find(&items).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get expiring items"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"items": items})
}

// UpdateItemQuantity 更新物品库存
func UpdateItemQuantity(c *gin.Context) {
	itemID := c.Param("id")
	
	var request struct {
		Quantity int `json:"quantity" binding:"min=0"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request data: " + err.Error()})
		return
	}
	
	// 获取物品
	var item models.Item
	if err := database.DB.First(&item, itemID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Item not found"})
		return
	}
	
	// 记录原始数量
	oldQuantity := item.Quantity
	
	// 更新库存
	if err := database.DB.Model(&item).Update("quantity", request.Quantity).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update quantity"})
		return
	}
	
	// 记录移动记录
	userID, exists := c.Get("user_id")
	if exists {
		quantityChange := request.Quantity - oldQuantity
		var movementType, reason string
		
		if quantityChange > 0 {
			movementType = "入库"
			reason = fmt.Sprintf("库存增加 %d", quantityChange)
		} else if quantityChange < 0 {
			movementType = "出库"
			reason = fmt.Sprintf("库存减少 %d", -quantityChange)
		} else {
			// 数量没有变化，不记录移动
			c.JSON(http.StatusOK, gin.H{
				"message": "Quantity unchanged",
				"old_quantity": oldQuantity,
				"new_quantity": request.Quantity,
			})
			return
		}
		
		movement := models.Movement{
			ItemID:       item.ID,
			MovementType: movementType,
			FromLocation: fmt.Sprintf("库存: %d %s", oldQuantity, item.Unit),
			ToLocation:   fmt.Sprintf("库存: %d %s", request.Quantity, item.Unit),
			Quantity:     quantityChange,
			Reason:       reason,
			Notes:        "通过库存管理界面手动调整",
			UserID:       userID.(uint),
		}
		if err := database.DB.Create(&movement).Error; err != nil {
			// 记录错误但不影响主要功能
			fmt.Printf("Failed to create movement record: %v\n", err)
		}
	}
	
	c.JSON(http.StatusOK, gin.H{
		"message": "Quantity updated successfully",
		"old_quantity": oldQuantity,
		"new_quantity": request.Quantity,
	})
}
