package main

import (
	"log"
	"central-storage-system/database"
	"central-storage-system/routes"
	"github.com/gin-gonic/gin"
)

func main() {
	// 初始化数据库
	database.InitDatabase()
	
	// 设置Gin模式
	gin.SetMode(gin.ReleaseMode)
	
	// 设置路由
	r := routes.SetupRoutes()
	
	log.Println("Server starting on port 8082...")
	log.Println("API documentation available at: http://localhost:8082/api/health")
	
	// 启动服务器
	if err := r.Run(":8082"); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
