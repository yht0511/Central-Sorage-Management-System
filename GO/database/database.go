package database

import (
	"central-storage-system/auth"
	"central-storage-system/models"
	"log"
	"os"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

// InitDatabase 初始化数据库连接
func InitDatabase() {
	var err error
	
	// 如果文件夹data不存在，则创建
	// 如果文件夹data不存在，则创建
	if _, err := os.Stat("data"); os.IsNotExist(err) {
		if err := os.Mkdir("data", 0755); err != nil {
			log.Fatal("Failed to create data directory:", err)
		}
	}

	// 如果数据库文件不存在，则创建空文件
	dbPath := "data/storage_system.db"
	if _, err := os.Stat(dbPath); os.IsNotExist(err) {
		file, err := os.Create(dbPath)
		if err != nil {
			log.Fatal("Failed to create database file:", err)
		}
		file.Close()
	}
	// 连接SQLite数据库
	DB, err = gorm.Open(sqlite.Open("data/storage_system.db"), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	
	log.Println("Database connection established")
	
	// 自动迁移表结构
	err = DB.AutoMigrate(
		&models.User{},
		&models.Laboratory{},
		&models.Storage{},
		&models.Section{},
		&models.Item{},
		&models.Movement{}, // 移动记录模型
	)
	
	if err != nil {
		log.Fatal("Failed to migrate database:", err)
	}
	
	log.Println("Database migration completed")
	
	// 创建默认管理员用户
	createDefaultAdmin()
}

// createDefaultAdmin 创建默认管理员用户
func createDefaultAdmin() {
	var user models.User
	result := DB.Where("username = ?", "admin").First(&user)
	
	if result.Error == gorm.ErrRecordNotFound {
		// 使用auth包加密密码
		hashedPassword, err := auth.HashPassword("admin123")
		if err != nil {
			log.Printf("Failed to hash password: %v", err)
			return
		}
		
		adminUser := models.User{
			Username: "admin",
			Email:    "admin@example.com",
			Password: hashedPassword,
			Role:     "admin",
			Active:   true,
		}
		
		if err := DB.Create(&adminUser).Error; err != nil {
			log.Printf("Failed to create default admin user: %v", err)
		} else {
			log.Println("Default admin user created: username=admin, password=admin123")
		}
	}
}
