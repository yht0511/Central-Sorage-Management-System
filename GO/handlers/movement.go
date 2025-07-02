package handlers

import (
	"central-storage-system/database"
	"central-storage-system/models"
	"encoding/csv"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
)

// GetMovements 获取移动记录
func GetMovements(c *gin.Context) {
	var req models.PaginationRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid query parameters: " + err.Error()})
		return
	}
	req.SetDefaults()

	var movements []models.Movement
	var total int64
	
	// 构建查询
	query := database.DB.Preload("Item").Preload("User")

	// 支持按用户ID过滤
	if userID := c.Query("user_id"); userID != "" {
		query = query.Where("user_id = ?", userID)
	}

	// 支持按移动类型过滤
	if movementType := c.Query("movement_type"); movementType != "" {
		query = query.Where("movement_type = ?", movementType)
	}

	// 支持按时间范围过滤
	if startDate := c.Query("start_date"); startDate != "" {
		query = query.Where("created_at >= ?", startDate)
	}
	if endDate := c.Query("end_date"); endDate != "" {
		query = query.Where("created_at <= ?", endDate+" 23:59:59")
	}

	// 支持按物品名称搜索
	if req.Search != "" {
		// 需要先查询物品ID
		var items []models.Item
		database.DB.Where("name LIKE ?", "%"+req.Search+"%").Find(&items)
		var itemIDs []uint
		for _, item := range items {
			itemIDs = append(itemIDs, item.ID)
		}
		if len(itemIDs) > 0 {
			query = query.Where("item_id IN ?", itemIDs)
		} else {
			// 如果没有匹配的物品，返回空结果
			query = query.Where("1 = 0")
		}
	}

	// 获取总数
	if err := query.Model(&models.Movement{}).Count(&total).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count movements"})
		return
	}

	// 排序和分页
	if err := query.Order("created_at DESC").Limit(req.PageSize).Offset(req.GetOffset()).Find(&movements).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get movements"})
		return
	}

	// 创建分页响应
	response := models.CreatePaginationResponse(movements, total, &req)
	c.JSON(http.StatusOK, response)
}

// CreateMovement 创建移动记录
func CreateMovement(c *gin.Context) {
	var movement models.Movement
	if err := c.ShouldBindJSON(&movement); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 获取当前用户ID
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}
	movement.UserID = userID.(uint)

	// 验证物品是否存在
	var item models.Item
	if err := database.DB.First(&item, movement.ItemID).Error; err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Item not found"})
		return
	}

	// 验证数量
	if movement.Quantity <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Quantity must be greater than 0"})
		return
	}

	// 根据移动类型验证和更新库存
	switch movement.MovementType {
	case "出库", "报废", "损坏":
		if item.Quantity < movement.Quantity {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Insufficient quantity"})
			return
		}
		item.Quantity -= movement.Quantity
	case "入库":
		item.Quantity += movement.Quantity
	case "转移":
		// 转移不改变总数量
	case "盘点":
		// 盘点可能调整数量
		if movement.Reason != "" {
			// 如果备注中包含调整信息，可以解析并更新
		}
	}

	// 开始事务
	tx := database.DB.Begin()

	// 保存移动记录
	if err := tx.Create(&movement).Error; err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create movement"})
		return
	}

	// 更新物品库存
	if err := tx.Save(&item).Error; err != nil {
		tx.Rollback()
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update item quantity"})
		return
	}

	tx.Commit()

	c.JSON(http.StatusCreated, gin.H{
		"message":  "Movement created successfully",
		"movement": movement,
	})
}

// ExportMovementsCSV 导出移动记录为CSV
func ExportMovementsCSV(c *gin.Context) {
	var movements []models.Movement
	query := database.DB.Preload("Item").Preload("User")

	// 支持相同的过滤条件
	if userID := c.Query("user_id"); userID != "" {
		query = query.Where("user_id = ?", userID)
	}
	if movementType := c.Query("movement_type"); movementType != "" {
		query = query.Where("movement_type = ?", movementType)
	}
	if startDate := c.Query("start_date"); startDate != "" {
		query = query.Where("created_at >= ?", startDate)
	}
	if endDate := c.Query("end_date"); endDate != "" {
		query = query.Where("created_at <= ?", endDate+" 23:59:59")
	}
	if search := c.Query("search"); search != "" {
		var items []models.Item
		database.DB.Where("name LIKE ?", "%"+search+"%").Find(&items)
		var itemIDs []uint
		for _, item := range items {
			itemIDs = append(itemIDs, item.ID)
		}
		if len(itemIDs) > 0 {
			query = query.Where("item_id IN ?", itemIDs)
		}
	}

	// 获取所有符合条件的记录（不分页）
	if err := query.Order("created_at DESC").Find(&movements).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get movements for export"})
		return
	}

	// 设置响应头
	filename := fmt.Sprintf("movements_export_%s.csv", time.Now().Format("20060102_150405"))
	c.Header("Content-Type", "text/csv; charset=utf-8")
	c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", filename))

	// 创建CSV写入器
	writer := csv.NewWriter(c.Writer)
	defer writer.Flush()

	// 写入BOM以支持Excel正确显示中文
	c.Writer.Write([]byte{0xEF, 0xBB, 0xBF})

	// 写入CSV头部
	headers := []string{
		"ID",
		"物品名称",
		"移动类型",
		"源位置",
		"目标位置",
		"数量",
		"原因",
		"备注",
		"操作人",
		"记录时间",
	}
	if err := writer.Write(headers); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to write CSV headers"})
		return
	}

	// 写入数据行
	for _, movement := range movements {
		record := []string{
			strconv.Itoa(int(movement.ID)),
			movement.Item.Name,
			movement.MovementType,
			movement.FromLocation,
			movement.ToLocation,
			strconv.Itoa(int(movement.Quantity)),
			movement.Reason,
			movement.Notes,
			getUserDisplayName(movement.User),
			movement.CreatedAt.Format("2006-01-02 15:04:05"),
		}
		if err := writer.Write(record); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to write CSV record"})
			return
		}
	}
}

// DeleteMovement 删除移动记录（仅管理员）
func DeleteMovement(c *gin.Context) {
	id := c.Param("id")
	
	var movement models.Movement
	if err := database.DB.First(&movement, id).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Movement not found"})
		return
	}

	if err := database.DB.Delete(&movement).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete movement"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Movement deleted successfully"})
}

// 辅助函数：获取用户显示名称
func getUserDisplayName(user models.User) string {
	if user.RealName != "" {
		return user.RealName
	}
	return user.Username
}
