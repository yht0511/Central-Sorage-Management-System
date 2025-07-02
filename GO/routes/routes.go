package routes

import (
	"central-storage-system/handlers"
	"central-storage-system/middleware"

	"github.com/gin-gonic/gin"
)

// SetupRoutes 设置所有路由
func SetupRoutes() *gin.Engine {
	r := gin.Default()
	
	// 添加CORS中间件
	r.Use(middleware.CORSMiddleware())
	
	// 公开路由
	public := r.Group("/api")
	{
		public.POST("/login", handlers.Login)
		public.GET("/health", func(c *gin.Context) {
			c.JSON(200, gin.H{"status": "ok"})
		})
	}
	
	// 需要认证的路由
	auth := r.Group("/api")
	auth.Use(middleware.AuthMiddleware())
	{
		// 用户相关
		auth.GET("/profile", handlers.GetProfile)
		auth.PUT("/profile", handlers.UpdateProfile)
		auth.POST("/change-password", handlers.ChangePassword)
		
		// 统计数据
		auth.GET("/stats/dashboard", handlers.GetDashboardStats)
		auth.GET("/stats/user", handlers.GetUserStats)
		
		// 实验室管理
		auth.GET("/laboratories", handlers.GetLaboratories)
		auth.GET("/laboratories/:id", handlers.GetLaboratory)
		auth.GET("/labs/:lab_id/storages", handlers.GetStoragesByLab)
		
		// 存储装置管理
		auth.GET("/storages", handlers.GetStorages)
		auth.GET("/storages/:id", handlers.GetStorage)
		auth.GET("/stores/:storage_id/sections", handlers.GetSectionsByStorage)
		
		// 分区管理
		auth.GET("/sections", handlers.GetSections)
		auth.GET("/sections/:id", handlers.GetSection)
		
		// 物品管理 - 普通用户有完整权限
		auth.GET("/items", handlers.GetItems)
		auth.GET("/items/:id", handlers.GetItem)
		auth.POST("/items", handlers.CreateItem)
		auth.PUT("/items/:id", handlers.UpdateItem)
		auth.DELETE("/items/:id", handlers.DeleteItem)
		auth.PUT("/items/:id/quantity", handlers.UpdateItemQuantity)
		auth.GET("/items/categories", handlers.GetCategories)
		auth.GET("/items/low-stock", handlers.GetLowStockItems)
		auth.GET("/items/expiring", handlers.GetExpiringItems)
		auth.GET("/items/check-code", handlers.CheckItemCodeExists)
		
		// 移动记录管理 - 普通用户只能查看
		auth.GET("/movements", handlers.GetMovements)
		auth.GET("/movements/export", handlers.ExportMovementsCSV)
	}
	
	// 需要管理员权限的路由
	admin := r.Group("/api/admin")
	admin.Use(middleware.AuthMiddleware())
	admin.Use(middleware.AdminMiddleware())
	{
		// 用户管理
		admin.POST("/register", handlers.Register)
		admin.GET("/users", handlers.GetUsers)
		admin.GET("/users/:id", handlers.GetUser)
		admin.PUT("/users/:id", handlers.UpdateUser)
		admin.DELETE("/users/:id", handlers.DeleteUser)
		
		// 实验室管理
		admin.POST("/laboratories", handlers.CreateLaboratory)
		admin.PUT("/laboratories/:id", handlers.UpdateLaboratory)
		admin.DELETE("/laboratories/:id", handlers.DeleteLaboratory)
		
		// 存储装置管理
		admin.POST("/storages", handlers.CreateStorage)
		admin.PUT("/storages/:id", handlers.UpdateStorage)
		admin.DELETE("/storages/:id", handlers.DeleteStorage)
		
		// 分区管理 - 仅管理员
		admin.POST("/sections", handlers.CreateSection)
		admin.PUT("/sections/:id", handlers.UpdateSection)
		admin.DELETE("/sections/:id", handlers.DeleteSection)
		
		// 移动记录管理 - 仅管理员可创建和删除
		admin.POST("/movements", handlers.CreateMovement)
		admin.DELETE("/movements/:id", handlers.DeleteMovement)
	}

	// 静态文件服务
	r.Static("/assets", "./dist/assets")
	r.StaticFile("/", "./dist/index.html")
	r.StaticFile("/index.html", "./dist/index.html")

	// 404返回index.html
	r.NoRoute(func(c *gin.Context) {
		c.File("./dist/index.html")
	})
	return r
}
