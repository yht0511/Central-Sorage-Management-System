package models

import (
	"database/sql/driver"
	"fmt"
	"strings"
	"time"

	"gorm.io/datatypes"
)

// CustomDate 自定义日期类型，支持 "2006-01-02" 格式
type CustomDate struct {
	time.Time
}

// UnmarshalJSON 自定义JSON反序列化
func (cd *CustomDate) UnmarshalJSON(data []byte) error {
	if len(data) == 0 || string(data) == "null" {
		return nil
	}
	
	// 去除引号
	dateStr := strings.Trim(string(data), `"`)
	if dateStr == "" {
		return nil
	}
	
	// 解析日期
	t, err := time.Parse("2006-01-02", dateStr)
	if err != nil {
		return err
	}
	
	cd.Time = t
	return nil
}

// MarshalJSON 自定义JSON序列化
func (cd CustomDate) MarshalJSON() ([]byte, error) {
	if cd.Time.IsZero() {
		return []byte("null"), nil
	}
	return []byte(fmt.Sprintf(`"%s"`, cd.Time.Format("2006-01-02"))), nil
}

// Scan 实现 sql.Scanner 接口
func (cd *CustomDate) Scan(value interface{}) error {
	if value == nil {
		cd.Time = time.Time{}
		return nil
	}
	
	switch v := value.(type) {
	case time.Time:
		cd.Time = v
	case string:
		t, err := time.Parse("2006-01-02", v)
		if err != nil {
			return err
		}
		cd.Time = t
	default:
		return fmt.Errorf("cannot scan %T into CustomDate", value)
	}
	
	return nil
}

// Value 实现 driver.Valuer 接口
func (cd CustomDate) Value() (driver.Value, error) {
	if cd.Time.IsZero() {
		return nil, nil
	}
	return cd.Time.Format("2006-01-02"), nil
}

// User 用户模型
type User struct {
	ID          uint      `json:"id" gorm:"primarykey"`
	Username    string    `json:"username" gorm:"unique;not null"`
	Email       string    `json:"email" gorm:"unique;not null"`
	Password    string    `json:"-" gorm:"not null"` // 密码不在JSON中返回
	Role        string    `json:"role" gorm:"default:user"` // admin, user
	Active      bool      `json:"active" gorm:"default:true"`
	RealName    string    `json:"real_name" gorm:"size:100"` // 真实姓名
	Phone       string    `json:"phone" gorm:"size:20"`      // 电话号码
	Department  string    `json:"department" gorm:"size:100"` // 部门
	Bio         string    `json:"bio" gorm:"type:text"`       // 个人简介
	LastLogin   time.Time `json:"last_login"`                 // 最后登录时间
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// Laboratory 实验室模型
type Laboratory struct {
	ID           uint      `json:"id" gorm:"primarykey"`
	Code         string    `json:"code" gorm:"not null"` // 实验室编号
	Name         string    `json:"name" gorm:"not null"`
	Location     string    `json:"location"`
	Description  string    `json:"description"`
	SecurityLevel int      `json:"security_level" gorm:"default:1"` // 1-5级安全等级
	Storages     []Storage `json:"storages" gorm:"foreignKey:LabID"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

// Storage 储存装置模型（如柜子）
type Storage struct {
	ID           uint      `json:"id" gorm:"primarykey"`
	Code         string    `json:"code" gorm:"not null"` // 储存装置编号
	Name         string    `json:"name" gorm:"not null"`
	Type         string    `json:"type"` // 柜子类型：零件柜、试剂柜等
	Location     string    `json:"location"`
	Description  string    `json:"description"`
	Status       string    `json:"status" gorm:"default:'运行中'"` // 运行中、维护中、停用
	Capacity     int       `json:"capacity" gorm:"default:0"` // 容量
	SecurityLevel int      `json:"security_level" gorm:"default:1"` // 1-5级安全等级
	Properties   datatypes.JSON `json:"properties" gorm:"type:json"` // 自定义属性
	LabID        uint      `json:"lab_id"`
	Laboratory   Laboratory `json:"laboratory" gorm:"foreignKey:LabID"`
	Sections     []Section  `json:"sections" gorm:"foreignKey:StorageID"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

// Section 最小存储单元模型（如抽屉）
type Section struct {
	ID           uint      `json:"id" gorm:"primarykey"`
	Code         string    `json:"code" gorm:"not null"` // 分区编号
	Name         string    `json:"name" gorm:"not null"`
	Position     string    `json:"position"` // 位置描述，如"第1层第2个抽屉"
	Description  string    `json:"description"`
	Status       string    `json:"status" gorm:"default:'可用'"` // 可用、已满、维护中、停用
	SecurityLevel int      `json:"security_level" gorm:"default:1"` // 1-5级安全等级
	Capacity     int       `json:"capacity" gorm:"default:100"` // 容量
	UsedCapacity int       `json:"used_capacity" gorm:"default:0"` // 已使用容量
	Properties   datatypes.JSON `json:"properties" gorm:"type:json"` // 自定义属性
	StorageID    uint      `json:"storage_id"`
	Storage      Storage   `json:"storage" gorm:"foreignKey:StorageID"`
	Items        []Item    `json:"items" gorm:"foreignKey:SectionID"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

// Item 物品模型
type Item struct {
	ID          uint                   `json:"id" gorm:"primarykey"`
	Code        string                 `json:"code" gorm:"not null"` // 物品编号
	Name        string                 `json:"name" gorm:"not null"`
	Description string                 `json:"description"`
	Category    string                 `json:"category"` // 种类：化学试剂、电子元件等
	Properties  map[string]interface{} `json:"properties" gorm:"serializer:json"` // 具体属性（JSON）
	Price       float64                `json:"price" gorm:"default:0"`
	Quantity    int                    `json:"quantity" gorm:"default:0"`
	MinQuantity int                    `json:"min_quantity" gorm:"default:0"` // 最小库存警告
	Unit        string                 `json:"unit"` // 单位：个、毫升、克等
	Supplier    string                 `json:"supplier"` // 供应商
	PurchaseDate *CustomDate           `json:"purchase_date"`
	ExpiryDate   *CustomDate           `json:"expiry_date"`
	SectionID   uint                   `json:"section_id"`
	Section     Section                `json:"section" gorm:"foreignKey:SectionID"`
	CreatedAt   time.Time              `json:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at"`
}

// LocationPath 位置路径信息
type LocationPath struct {
	LabCode     string `json:"lab_code"`
	LabName     string `json:"lab_name"`
	StorageCode string `json:"storage_code"`
	StorageName string `json:"storage_name"`
	SectionCode string `json:"section_code"`
	SectionName string `json:"section_name"`
	FullPath    string `json:"full_path"`
}

// PaginationRequest 分页请求结构
type PaginationRequest struct {
	Page     int    `form:"page"`        // 页码，从1开始
	PageSize int    `form:"page_size"`   // 页面大小，最大100
	Search   string `form:"search"`      // 搜索关键词
	SortBy   string `form:"sort_by"`     // 排序字段
	SortDesc bool   `form:"sort_desc"`   // 是否降序
}

// PaginationResponse 分页响应结构
type PaginationResponse struct {
	Data       interface{} `json:"data"`        // 数据列表
	Total      int64       `json:"total"`       // 总记录数
	Page       int         `json:"page"`        // 当前页码
	PageSize   int         `json:"page_size"`   // 页面大小
	TotalPages int         `json:"total_pages"` // 总页数
	HasNext    bool        `json:"has_next"`    // 是否有下一页
	HasPrev    bool        `json:"has_prev"`    // 是否有上一页
}

// SetDefaults 设置分页请求的默认值
func (p *PaginationRequest) SetDefaults() {
	if p.Page <= 0 {
		p.Page = 1
	}
	if p.PageSize <= 0 {
		p.PageSize = 20
	}
	if p.PageSize > 100 {
		p.PageSize = 100
	}
}

// GetOffset 计算偏移量
func (p *PaginationRequest) GetOffset() int {
	return (p.Page - 1) * p.PageSize
}

// CreatePaginationResponse 创建分页响应
func CreatePaginationResponse(data interface{}, total int64, req *PaginationRequest) *PaginationResponse {
	totalPages := int((total + int64(req.PageSize) - 1) / int64(req.PageSize))
	
	return &PaginationResponse{
		Data:       data,
		Total:      total,
		Page:       req.Page,
		PageSize:   req.PageSize,
		TotalPages: totalPages,
		HasNext:    req.Page < totalPages,
		HasPrev:    req.Page > 1,
	}
}

// Movement 移动记录模型（新版本，更完整的移动记录）
type Movement struct {
	ID           uint      `json:"id" gorm:"primarykey"`
	ItemID       uint      `json:"item_id" gorm:"not null"`
	Item         Item      `json:"item" gorm:"foreignKey:ItemID"`
	MovementType string    `json:"movement_type" gorm:"not null"` // 入库、出库、转移、盘点、损坏、报废
	FromLocation string    `json:"from_location"`                 // 源位置描述
	ToLocation   string    `json:"to_location"`                   // 目标位置描述
	Quantity     int       `json:"quantity" gorm:"not null"`      // 移动数量
	Reason       string    `json:"reason" gorm:"not null"`        // 移动原因
	Notes        string    `json:"notes"`                         // 备注
	UserID       uint      `json:"user_id" gorm:"not null"`       // 操作人ID
	User         User      `json:"user" gorm:"foreignKey:UserID"` // 操作人
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}
