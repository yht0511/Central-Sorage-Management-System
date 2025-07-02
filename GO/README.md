# 实验室仓储管理系统

这是一个基于 Go 和 Gin 框架的实验室仓储管理系统后端 API。

## 系统架构

### 数据模型

系统采用三层拓扑结构：

1. **Laboratory（实验室）** - 顶级容器
2. **Storage（存储装置）** - 中级容器（如柜子、架子）
3. **Section（分区）** - 最小存储单元（如抽屉、格子）
4. **Item（物品）** - 存储的物品

### 功能特性

- ✅ 用户身份验证（JWT）
- ✅ 角色权限管理（管理员/普通用户）
- ✅ 三层拓扑存储结构管理
- ✅ 物品增删改查
- ✅ 库存管理和移动记录
- ✅ 低库存警告
- ✅ 过期物品提醒
- ✅ 安全等级管理（1-5 级）
- ✅ 完整的 API 接口

## 快速开始

### 1. 安装依赖

```bash
go mod tidy
```

### 2. 运行服务器

```bash
go run main.go
```

服务器将在 `http://localhost:8080` 启动。

### 3. 默认管理员账户

- 用户名: `admin`
- 密码: `admin123`

## API 接口

### 认证接口

#### 登录

```http
POST /api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

#### 获取用户信息

```http
GET /api/profile
Authorization: Bearer <token>
```

### 实验室管理

#### 获取所有实验室

```http
GET /api/laboratories
Authorization: Bearer <token>
```

#### 创建实验室（管理员）

```http
POST /api/admin/laboratories
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "LAB001",
  "name": "化学实验室",
  "location": "A栋2楼",
  "description": "主要用于化学实验",
  "security_level": 3
}
```

### 存储装置管理

#### 获取存储装置

```http
GET /api/storages
Authorization: Bearer <token>
```

#### 根据实验室获取存储装置

```http
GET /api/laboratories/1/storages
Authorization: Bearer <token>
```

#### 创建存储装置（管理员）

```http
POST /api/admin/storages
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "STORAGE001",
  "name": "试剂柜A",
  "type": "试剂柜",
  "location": "北墙",
  "description": "存放化学试剂",
  "security_level": 3,
  "lab_id": 1
}
```

### 分区管理

#### 获取分区

```http
GET /api/sections
Authorization: Bearer <token>
```

#### 根据存储装置获取分区

```http
GET /api/storages/1/sections
Authorization: Bearer <token>
```

#### 创建分区（管理员）

```http
POST /api/admin/sections
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "SEC001",
  "name": "第1层第1格",
  "position": "上层左侧",
  "description": "存放酸性试剂",
  "security_level": 3,
  "capacity": 50,
  "storage_id": 1
}
```

### 物品管理

#### 获取物品

```http
GET /api/items
Authorization: Bearer <token>

# 支持查询参数:
# - section_id: 按分区过滤
# - category: 按类别过滤
# - search: 按名称搜索
# - low_stock: 低库存物品
```

#### 获取低库存物品

```http
GET /api/items/low-stock
Authorization: Bearer <token>
```

#### 获取即将过期物品

```http
GET /api/items/expiring?days=30
Authorization: Bearer <token>
```

#### 创建物品（管理员）

```http
POST /api/admin/items
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "ITEM001",
  "name": "盐酸",
  "description": "分析纯盐酸",
  "category": "化学试剂",
  "properties": {
    "concentration": "37%",
    "purity": "AR",
    "cas": "7647-01-0"
  },
  "price": 25.50,
  "quantity": 10,
  "min_quantity": 2,
  "unit": "瓶",
  "supplier": "国药试剂",
  "section_id": 1
}
```

#### 获取物品移动记录

```http
GET /api/movements
Authorization: Bearer <token>

# 支持查询参数:
# - item_id: 按物品过滤
# - start_date: 开始日期 (YYYY-MM-DD)
# - end_date: 结束日期 (YYYY-MM-DD)
```

## 数据库设计

### 表结构

1. **users** - 用户表
2. **laboratories** - 实验室表
3. **storages** - 存储装置表
4. **sections** - 分区表
5. **items** - 物品表
6. **item_movements** - 物品移动记录表

### 安全等级

系统支持 1-5 级安全等级：

- 1 级：公开访问（任何人都可以接触）
- 2 级：低保密性（一般工作人员可访问）
- 3 级：中等保密性（授权人员可访问）
- 4 级：高保密性（特定权限人员可访问）
- 5 级：极端保密（最高权限人员可访问）

## 开发说明

### 项目结构

```
central-storage-system/
├── main.go                 # 主程序入口
├── go.mod                  # Go模块定义
├── models/                 # 数据模型
│   └── models.go
├── database/               # 数据库连接
│   └── database.go
├── auth/                   # 身份验证
│   └── auth.go
├── middleware/             # 中间件
│   └── middleware.go
├── handlers/               # API处理器
│   ├── auth.go
│   ├── laboratory.go
│   ├── storage.go
│   ├── section.go
│   └── item.go
├── routes/                 # 路由配置
│   └── routes.go
└── README.md
```

### 扩展功能建议

1. **报表统计** - 添加物品统计、库存报表等功能
2. **条码管理** - 为物品生成和扫描条码
3. **图片上传** - 为物品添加图片支持
4. **通知系统** - 低库存和过期提醒通知
5. **审计日志** - 详细的操作日志记录
6. **批量操作** - 批量导入/导出物品信息

## 注意事项

1. 请在生产环境中修改 JWT 密钥
2. 建议使用更安全的密码策略
3. 可以考虑使用 PostgreSQL 或 MySQL 替代 SQLite
4. 建议添加数据备份策略
