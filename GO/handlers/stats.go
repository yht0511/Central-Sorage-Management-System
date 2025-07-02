package handlers

import (
	"central-storage-system/database"
	"central-storage-system/models"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// GetDashboardStats 获取仪表盘统计数据
func GetDashboardStats(c *gin.Context) {
	stats := make(gin.H)

	// 获取实验室数量
	var labCount int64
	database.DB.Model(&models.Laboratory{}).Count(&labCount)
	stats["laboratories"] = labCount

	// 获取存储装置数量
	var storageCount int64
	database.DB.Model(&models.Storage{}).Count(&storageCount)
	stats["storages"] = storageCount

	// 获取分区数量
	var sectionCount int64
	database.DB.Model(&models.Section{}).Count(&sectionCount)
	stats["sections"] = sectionCount

	// 获取物品数量
	var itemCount int64
	database.DB.Model(&models.Item{}).Count(&itemCount)
	stats["items"] = itemCount

	// 获取低库存物品数量
	var lowStockCount int64
	database.DB.Model(&models.Item{}).Where("quantity <= min_quantity").Count(&lowStockCount)
	stats["lowStockItems"] = lowStockCount

	// 获取即将过期物品数量（30天内）
	var expiringCount int64
	futureDate := time.Now().AddDate(0, 0, 30)
	database.DB.Model(&models.Item{}).Where("expiry_date IS NOT NULL AND expiry_date <= ?", futureDate).Count(&expiringCount)
	stats["expiringItems"] = expiringCount

	// 获取已过期物品数量
	var expiredCount int64
	now := time.Now()
	database.DB.Model(&models.Item{}).Where("expiry_date IS NOT NULL AND expiry_date < ?", now).Count(&expiredCount)
	stats["expiredItems"] = expiredCount

	// 获取用户数量
	var userCount int64
	database.DB.Model(&models.User{}).Count(&userCount)
	stats["users"] = userCount

	// 获取最近7天的移动记录数量
	var recentMovements int64
	weekAgo := time.Now().AddDate(0, 0, -7)
	database.DB.Model(&models.Movement{}).Where("created_at >= ?", weekAgo).Count(&recentMovements)
	stats["recentMovements"] = recentMovements

	c.JSON(http.StatusOK, stats)
}

// GetUserStats 获取用户个人统计数据
func GetUserStats(c *gin.Context) {
	userID, _ := c.Get("user_id")
	
	stats := make(gin.H)

	// 获取用户的移动记录数量
	var movementCount int64
	database.DB.Model(&models.Movement{}).Where("user_id = ?", userID).Count(&movementCount)
	stats["total_movements"] = movementCount
	stats["movements"] = movementCount // 向后兼容

	// 获取用户最近7天的活动数量
	var recentActivity int64
	weekAgo := time.Now().AddDate(0, 0, -7)
	database.DB.Model(&models.Movement{}).Where("user_id = ? AND created_at >= ?", userID, weekAgo).Count(&recentActivity)
	stats["recentActivity"] = recentActivity

	// 获取用户入库操作数量
	var inCount int64
	database.DB.Model(&models.Movement{}).Where("user_id = ? AND movement_type = ?", userID, "入库").Count(&inCount)
	stats["total_items"] = inCount
	stats["itemsCreated"] = inCount // 向后兼容

	// 获取用户可访问的实验室数量（简化为总数）
	var labCount int64
	database.DB.Model(&models.Laboratory{}).Count(&labCount)
	stats["labs_count"] = labCount

	// 获取用户可访问的存储装置数量（简化为总数）
	var deviceCount int64
	database.DB.Model(&models.Storage{}).Count(&deviceCount)
	stats["devices_count"] = deviceCount

	c.JSON(http.StatusOK, stats)
}
