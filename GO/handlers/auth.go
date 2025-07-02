package handlers

import (
	"central-storage-system/auth"
	"central-storage-system/database"
	"central-storage-system/models"
	"net/http"

	"github.com/gin-gonic/gin"
)

// LoginRequest 登录请求结构
type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

// RegisterRequest 注册请求结构
type RegisterRequest struct {
	Username string `json:"username" binding:"required"`
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=6"`
}

// Login 用户登录
func Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	var user models.User
	if err := database.DB.Where("username = ? AND active = ?", req.Username, true).First(&user).Error; err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}
	
	if !auth.CheckPassword(req.Password, user.Password) {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}
	
	token, err := auth.GenerateToken(user.ID, user.Username, user.Role)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"token": token,
		"user": gin.H{
			"id":       user.ID,
			"username": user.Username,
			"email":    user.Email,
			"role":     user.Role,
		},
	})
}

// Register 用户注册（仅管理员可用）
func Register(c *gin.Context) {
	var req RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// 检查用户名是否已存在
	var existingUser models.User
	if err := database.DB.Where("username = ?", req.Username).First(&existingUser).Error; err == nil {
		c.JSON(http.StatusConflict, gin.H{"error": "Username already exists"})
		return
	}
	
	// 检查邮箱是否已存在
	if err := database.DB.Where("email = ?", req.Email).First(&existingUser).Error; err == nil {
		c.JSON(http.StatusConflict, gin.H{"error": "Email already exists"})
		return
	}
	
	// 加密密码
	hashedPassword, err := auth.HashPassword(req.Password)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
		return
	}
	
	user := models.User{
		Username: req.Username,
		Email:    req.Email,
		Password: hashedPassword,
		Role:     "user",
		Active:   true,
	}
	
	if err := database.DB.Create(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
		return
	}
	
	c.JSON(http.StatusCreated, gin.H{
		"message": "User created successfully",
		"user": gin.H{
			"id":       user.ID,
			"username": user.Username,
			"email":    user.Email,
			"role":     user.Role,
		},
	})
}

// GetProfile 获取用户信息
func GetProfile(c *gin.Context) {
	userID, _ := c.Get("user_id")
	
	var user models.User
	if err := database.DB.First(&user, userID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"user": gin.H{
			"id":         user.ID,
			"username":   user.Username,
			"email":      user.Email,
			"role":       user.Role,
			"real_name":  user.RealName,
			"phone":      user.Phone,
			"department": user.Department,
			"bio":        user.Bio,
			"created_at": user.CreatedAt,
		},
	})
}

// UpdateProfile 更新用户信息
func UpdateProfile(c *gin.Context) {
	userID, _ := c.Get("user_id")
	
	var user models.User
	if err := database.DB.First(&user, userID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}
	
	var req struct {
		Email      string `json:"email"`
		RealName   string `json:"real_name"`
		Phone      string `json:"phone"`
		Department string `json:"department"`
		Bio        string `json:"bio"`
	}
	
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// 更新用户信息
	if req.Email != "" {
		user.Email = req.Email
	}
	user.RealName = req.RealName
	user.Phone = req.Phone
	user.Department = req.Department
	user.Bio = req.Bio
	
	if err := database.DB.Save(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update user"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"message": "Profile updated successfully",
		"user": gin.H{
			"id":         user.ID,
			"username":   user.Username,
			"email":      user.Email,
			"role":       user.Role,
			"real_name":  user.RealName,
			"phone":      user.Phone,
			"department": user.Department,
			"bio":        user.Bio,
		},
	})
}

// ChangePassword 修改密码
func ChangePassword(c *gin.Context) {
	userID, _ := c.Get("user_id")
	
	var req struct {
		OldPassword string `json:"old_password" binding:"required"`
		NewPassword string `json:"new_password" binding:"required,min=6"`
	}
	
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	var user models.User
	if err := database.DB.First(&user, userID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}
	
	if !auth.CheckPassword(req.OldPassword, user.Password) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid old password"})
		return
	}
	
	hashedPassword, err := auth.HashPassword(req.NewPassword)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
		return
	}
	
	user.Password = hashedPassword
	if err := database.DB.Save(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update password"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"message": "Password changed successfully"})
}

// GetUsers 获取用户列表（管理员）
func GetUsers(c *gin.Context) {
	var req models.PaginationRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid query parameters: " + err.Error()})
		return
	}
	req.SetDefaults()

	var users []models.User
	var total int64
	
	// 构建查询
	query := database.DB.Model(&models.User{}).Select("id, username, email, role, active, real_name, phone, department, created_at, updated_at")
	
	// 支持搜索
	if req.Search != "" {
		query = query.Where("username LIKE ? OR email LIKE ? OR real_name LIKE ?", 
			"%"+req.Search+"%", "%"+req.Search+"%", "%"+req.Search+"%")
	}
	
	// 支持按角色筛选
	if role := c.Query("role"); role != "" {
		query = query.Where("role = ?", role)
	}
	
	// 支持按状态筛选
	if active := c.Query("active"); active != "" {
		if active == "true" {
			query = query.Where("active = ?", true)
		} else if active == "false" {
			query = query.Where("active = ?", false)
		}
	}
	
	// 获取总数
	if err := query.Count(&total).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to count users"})
		return
	}
	
	// 分页查询
	if err := query.Order("created_at DESC").Limit(req.PageSize).Offset(req.GetOffset()).Find(&users).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get users"})
		return
	}
	
	// 创建分页响应
	response := models.CreatePaginationResponse(users, total, &req)
	c.JSON(http.StatusOK, response)
}

// GetUser 获取单个用户详情（管理员）
func GetUser(c *gin.Context) {
	id := c.Param("id")
	
	var user models.User
	if err := database.DB.Select("id, username, email, role, active, created_at").First(&user, id).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"user": user})
}

// UpdateUser 更新用户信息（管理员）
func UpdateUser(c *gin.Context) {
	id := c.Param("id")
	
	var user models.User
	if err := database.DB.First(&user, id).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}
	
	var req struct {
		Email      string `json:"email"`
		RealName   string `json:"real_name"`
		Phone      string `json:"phone"`
		Department string `json:"department"`
		Bio        string `json:"bio"`
		Role       string `json:"role"`
		Active     bool   `json:"active"`
	}
	
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	// 更新字段
	if req.Email != "" {
		user.Email = req.Email
	}
	if req.RealName != "" {
		user.RealName = req.RealName
	}
	if req.Phone != "" {
		user.Phone = req.Phone
	}
	if req.Department != "" {
		user.Department = req.Department
	}
	if req.Bio != "" {
		user.Bio = req.Bio
	}
	if req.Role != "" {
		user.Role = req.Role
	}
	user.Active = req.Active
	
	if err := database.DB.Save(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update user"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"message": "User updated successfully",
		"user": gin.H{
			"id":         user.ID,
			"username":   user.Username,
			"email":      user.Email,
			"real_name":  user.RealName,
			"phone":      user.Phone,
			"department": user.Department,
			"bio":        user.Bio,
			"role":       user.Role,
			"active":     user.Active,
		},
	})
}

// DeleteUser 删除用户（管理员）
func DeleteUser(c *gin.Context) {
	id := c.Param("id")
	
	var user models.User
	if err := database.DB.First(&user, id).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}
	
	// 不能删除自己
	userID, _ := c.Get("user_id")
	if user.ID == userID.(uint) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Cannot delete yourself"})
		return
	}
	
	if err := database.DB.Delete(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete user"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{"message": "User deleted successfully"})
}
