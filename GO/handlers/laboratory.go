package handlers

import (
	"central-storage-system/database"
	"central-storage-system/models"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

// GetLaboratories 获取所有实验室（支持分页和搜索）
func GetLaboratories(c *gin.Context) {
	var req models.PaginationRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid query parameters: " + err.Error()})
		return
	}
	req.SetDefaults()

	var laboratories []models.Laboratory
	var total int64
	
	// 构建查询
	query := database.DB.Preload("Storages")
	
	// 搜索功能
	if req.Search != "" {
		searchTerm := "%" + req.Search + "%"
		query = query.Where("name LIKE ? OR code LIKE ? OR location LIKE ? OR description LIKE ?", 
			searchTerm, searchTerm, searchTerm, searchTerm)
	}
	
	// 支持按安全等级过滤
	if securityLevel := c.Query("security_level"); securityLevel != "" {
		query = query.Where("security_level = ?", securityLevel)
	}
	
	// 获取总数
	if err := query.Model(&models.Laboratory{}).Count(&total).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count laboratories"})
		return
	}
	
	// 排序
	orderBy := "created_at DESC" // 默认排序
	if req.SortBy != "" {
		allowedSorts := map[string]bool{
			"name": true, "code": true, "location": true, "security_level": true,
			"created_at": true, "updated_at": true,
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
	if err := query.Order(orderBy).Limit(req.PageSize).Offset(req.GetOffset()).Find(&laboratories).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get laboratories"})
		return
	}
	
	// 创建分页响应
	response := models.CreatePaginationResponse(laboratories, total, &req)
	c.JSON(http.StatusOK, response)
}

// GetLaboratory 获取单个实验室详情
func GetLaboratory(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid laboratory ID"})
		return
	}
	
	var laboratory models.Laboratory
	if err := database.DB.Preload("Storages.Sections.Items").First(&laboratory, uint(id)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Laboratory not found"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"laboratory": laboratory})
}

// CreateLaboratory 创建实验室
func CreateLaboratory(c *gin.Context) {
	var laboratory models.Laboratory
	if err := c.ShouldBindJSON(&laboratory); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	if err := database.DB.Create(&laboratory).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create laboratory"})
		return
	}
	
	c.JSON(http.StatusCreated, gin.H{"laboratory": laboratory})
}

// UpdateLaboratory 更新实验室
func UpdateLaboratory(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid laboratory ID"})
		return
	}
	
	var laboratory models.Laboratory
	if err := database.DB.First(&laboratory, uint(id)).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Laboratory not found"})
		return
	}
	
	if err := c.ShouldBindJSON(&laboratory); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	if err := database.DB.Save(&laboratory).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update laboratory"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"laboratory": laboratory})
}

// DeleteLaboratory 删除实验室
func DeleteLaboratory(c *gin.Context) {
	id, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid laboratory ID"})
		return
	}
	
	// 检查是否存在关联的存储装置
	var count int64
	database.DB.Model(&models.Storage{}).Where("lab_id = ?", uint(id)).Count(&count)
	if count > 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Cannot delete laboratory with existing storages"})
		return
	}
	
	if err := database.DB.Delete(&models.Laboratory{}, uint(id)).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete laboratory"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"message": "Laboratory deleted successfully"})
}
