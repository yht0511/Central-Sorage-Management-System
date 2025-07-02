package handlers

import (
	"central-storage-system/database"
	"central-storage-system/models"
	"fmt"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"gorm.io/datatypes"
)

// GetSections 获取所有分区（支持分页和搜索）
func GetSections(c *gin.Context) {
	var req models.PaginationRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid query parameters: " + err.Error()})
		return
	}
	req.SetDefaults()

	var sections []models.Section
	var total int64
	
	// 构建查询
	query := database.DB.Preload("Storage.Laboratory").Preload("Items")
	
	// 搜索功能
	if req.Search != "" {
		searchTerm := "%" + req.Search + "%"
		query = query.Where("name LIKE ? OR code LIKE ? OR position LIKE ? OR description LIKE ?", 
			searchTerm, searchTerm, searchTerm, searchTerm)
	}
	
	// 支持按存储装置ID过滤
	if storageID := c.Query("storage_id"); storageID != "" {
		query = query.Where("storage_id = ?", storageID)
	}
	
	// 支持按实验室ID过滤
	if laboratoryID := c.Query("laboratory_id"); laboratoryID != "" {
		query = query.Joins("JOIN storages ON sections.storage_id = storages.id").
			Where("storages.lab_id = ?", laboratoryID)
	}
	
	// 支持按状态过滤
	if status := c.Query("status"); status != "" {
		query = query.Where("status = ?", status)
	}
	
	// 支持按安全等级过滤
	if securityLevel := c.Query("security_level"); securityLevel != "" {
		query = query.Where("security_level = ?", securityLevel)
	}
	
	// 支持按容量使用率过滤
	if capacityFilter := c.Query("capacity_filter"); capacityFilter != "" {
		switch capacityFilter {
		case "full":
			query = query.Where("used_capacity >= capacity")
		case "high":
			query = query.Where("used_capacity >= capacity * 0.8")
		case "low":
			query = query.Where("used_capacity < capacity * 0.3")
		}
	}
	
	// 获取总数
	if err := query.Model(&models.Section{}).Count(&total).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count sections"})
		return
	}
	
	// 排序
	orderBy := "created_at DESC" // 默认排序
	if req.SortBy != "" {
		allowedSorts := map[string]bool{
			"name": true, "code": true, "position": true, "status": true, "capacity": true,
			"used_capacity": true, "security_level": true, "created_at": true, "updated_at": true,
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
	if err := query.Order(orderBy).Limit(req.PageSize).Offset(req.GetOffset()).Find(&sections).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get sections"})
		return
	}
	
	// 创建分页响应
	response := models.CreatePaginationResponse(sections, total, &req)
	c.JSON(http.StatusOK, response)
}

// GetSectionsByStorage 根据存储装置ID获取分区
func GetSectionsByStorage(c *gin.Context) {
	storageID, err := strconv.ParseUint(c.Param("storage_id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid storage ID"})
		return
	}
	
	var sections []models.Section
	if err := database.DB.Where("storage_id = ?", uint(storageID)).Find(&sections).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get sections"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"sections": sections})
}

// GetSection 获取单个分区详情
func GetSection(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid section ID"})
		return
	}
	
	var section models.Section
	if err := database.DB.Preload("Storage.Laboratory").Preload("Items").First(&section, uint(id)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Section not found"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"section": section})
}

// CreateSection 创建分区
func CreateSection(c *gin.Context) {
	var section models.Section
	if err := c.ShouldBindJSON(&section); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// 添加调试日志
	fmt.Printf("Creating section: %+v\n", section)
	fmt.Printf("StorageID: %d\n", section.StorageID)
	
	// 验证存储装置是否存在
	var storage models.Storage
	if err := database.DB.First(&storage, section.StorageID).Error; err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Storage not found"})
		return
	}
	
	if err := database.DB.Create(&section).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create section"})
		return
	}
	
	// 重新查询以获取关联数据
	database.DB.Preload("Storage.Laboratory").First(&section, section.ID)
	
	c.JSON(http.StatusCreated, gin.H{"section": section})
}

// UpdateSection 更新分区
func UpdateSection(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid section ID"})
		return
	}
	
	var section models.Section
	if err := database.DB.First(&section, uint(id)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Section not found"})
		return
	}
	
	// 创建更新数据结构
	var updateData struct {
		Code          string         `json:"code"`
		Name          string         `json:"name"`
		Position      string         `json:"position"`
		Description   string         `json:"description"`
		Status        string         `json:"status"`
		SecurityLevel int            `json:"security_level"`
		Capacity      int            `json:"capacity"`
		UsedCapacity  int            `json:"used_capacity"`
		Properties    datatypes.JSON `json:"properties"`
		StorageID     uint           `json:"storage_id"`
	}
	
	if err := c.ShouldBindJSON(&updateData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// 如果修改了存储装置ID，验证新存储装置是否存在
	if updateData.StorageID != 0 {
		var storage models.Storage
		if err := database.DB.First(&storage, updateData.StorageID).Error; err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Storage not found"})
			return
		}
	}
	
	// 更新分区数据
	section.Code = updateData.Code
	section.Name = updateData.Name
	section.Position = updateData.Position
	section.Description = updateData.Description
	section.Status = updateData.Status
	section.SecurityLevel = updateData.SecurityLevel
	section.Capacity = updateData.Capacity
	section.UsedCapacity = updateData.UsedCapacity
	section.Properties = updateData.Properties // 确保Properties被正确更新
	section.StorageID = updateData.StorageID
	
	if err := database.DB.Save(&section).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update section"})
		return
	}
	
	// 重新查询以获取关联数据
	database.DB.Preload("Storage.Laboratory").First(&section, section.ID)
	
	c.JSON(http.StatusOK, gin.H{"section": section})
}

// DeleteSection 删除分区
func DeleteSection(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid section ID"})
		return
	}
	
	// 检查是否存在关联的物品
	var count int64
	database.DB.Model(&models.Item{}).Where("section_id = ?", uint(id)).Count(&count)
	if count > 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Cannot delete section with existing items"})
		return
	}
	
	if err := database.DB.Delete(&models.Section{}, uint(id)).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete section"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"message": "Section deleted successfully"})
}
