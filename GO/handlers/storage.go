package handlers

import (
	"central-storage-system/database"
	"central-storage-system/models"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"gorm.io/datatypes"
)

// GetStorages 获取所有存储装置（支持分页和搜索）
func GetStorages(c *gin.Context) {
	var req models.PaginationRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid query parameters: " + err.Error()})
		return
	}
	req.SetDefaults()

	var storages []models.Storage
	var total int64
	
	// 构建查询
	query := database.DB.Preload("Laboratory").Preload("Sections")
	
	// 搜索功能
	if req.Search != "" {
		searchTerm := "%" + req.Search + "%"
		query = query.Where("name LIKE ? OR code LIKE ? OR type LIKE ? OR location LIKE ? OR description LIKE ?", 
			searchTerm, searchTerm, searchTerm, searchTerm, searchTerm)
	}
	
	// 支持按实验室ID过滤
	if labID := c.Query("lab_id"); labID != "" {
		query = query.Where("lab_id = ?", labID)
	}
	
	// 支持按类型过滤
	if storageType := c.Query("type"); storageType != "" {
		query = query.Where("type = ?", storageType)
	}
	
	// 支持按状态过滤
	if status := c.Query("status"); status != "" {
		query = query.Where("status = ?", status)
	}
	
	// 支持按安全等级过滤
	if securityLevel := c.Query("security_level"); securityLevel != "" {
		query = query.Where("security_level = ?", securityLevel)
	}
	
	// 获取总数
	if err := query.Model(&models.Storage{}).Count(&total).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count storages"})
		return
	}
	
	// 排序
	orderBy := "created_at DESC" // 默认排序
	if req.SortBy != "" {
		allowedSorts := map[string]bool{
			"name": true, "code": true, "type": true, "status": true, "capacity": true,
			"security_level": true, "created_at": true, "updated_at": true,
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
	if err := query.Order(orderBy).Limit(req.PageSize).Offset(req.GetOffset()).Find(&storages).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get storages"})
		return
	}
	
	// 创建分页响应
	response := models.CreatePaginationResponse(storages, total, &req)
	c.JSON(http.StatusOK, response)
}

// GetStoragesByLab 根据实验室ID获取存储装置
func GetStoragesByLab(c *gin.Context) {
	labID, err := strconv.ParseUint(c.Param("lab_id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid laboratory ID"})
		return
	}
	
	var storages []models.Storage
	if err := database.DB.Where("lab_id = ?", uint(labID)).Preload("Sections").Find(&storages).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get storages"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"storages": storages})
}

// GetStorage 获取单个存储装置详情
func GetStorage(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid storage ID"})
		return
	}
	
	var storage models.Storage
	if err := database.DB.Preload("Laboratory").Preload("Sections.Items").First(&storage, uint(id)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Storage not found"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"storage": storage})
}

// CreateStorage 创建存储装置
func CreateStorage(c *gin.Context) {
	var storage models.Storage
	if err := c.ShouldBindJSON(&storage); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// 验证实验室是否存在
	var laboratory models.Laboratory
	if err := database.DB.First(&laboratory, storage.LabID).Error; err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Laboratory not found"})
		return
	}
	
	if err := database.DB.Create(&storage).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create storage"})
		return
	}
	
	// 重新查询以获取关联数据
	database.DB.Preload("Laboratory").First(&storage, storage.ID)
	
	c.JSON(http.StatusCreated, gin.H{"storage": storage})
}

// UpdateStorage 更新存储装置
func UpdateStorage(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid storage ID"})
		return
	}
	
	var storage models.Storage
	if err := database.DB.First(&storage, uint(id)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Storage not found"})
		return
	}
	
	// 创建更新数据结构
	var updateData struct {
		Code          string         `json:"code"`
		Name          string         `json:"name"`
		Type          string         `json:"type"`
		Location      string         `json:"location"`
		Description   string         `json:"description"`
		Status        string         `json:"status"`
		Capacity      int            `json:"capacity"`
		SecurityLevel int            `json:"security_level"`
		Properties    datatypes.JSON `json:"properties"`
		LabID         uint           `json:"lab_id"`
	}
	
	if err := c.ShouldBindJSON(&updateData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// 如果修改了实验室ID，验证新实验室是否存在
	if updateData.LabID != 0 {
		var laboratory models.Laboratory
		if err := database.DB.First(&laboratory, updateData.LabID).Error; err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Laboratory not found"})
			return
		}
	}
	
	// 更新存储装置数据
	storage.Code = updateData.Code
	storage.Name = updateData.Name
	storage.Type = updateData.Type
	storage.Location = updateData.Location
	storage.Description = updateData.Description
	storage.Status = updateData.Status
	storage.Capacity = updateData.Capacity
	storage.SecurityLevel = updateData.SecurityLevel
	storage.Properties = updateData.Properties // 确保Properties被正确更新
	storage.LabID = updateData.LabID
	
	if err := database.DB.Save(&storage).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update storage"})
		return
	}
	
	// 重新查询以获取关联数据
	database.DB.Preload("Laboratory").First(&storage, storage.ID)
	
	c.JSON(http.StatusOK, gin.H{"storage": storage})
}

// DeleteStorage 删除存储装置
func DeleteStorage(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid storage ID"})
		return
	}
	
	// 检查是否存在关联的分区
	var count int64
	database.DB.Model(&models.Section{}).Where("storage_id = ?", uint(id)).Count(&count)
	if count > 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Cannot delete storage with existing sections"})
		return
	}
	
	if err := database.DB.Delete(&models.Storage{}, uint(id)).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete storage"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"message": "Storage deleted successfully"})
}
