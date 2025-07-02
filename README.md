# Central Storage System

一个基于 Go 后端和 Vue.js 前端的现代化中央存储管理系统。

## 功能特性

- 🏢 实验室管理
- 📦 物品存储管理
- 🔄 移动历史记录
- 👥 用户权限管理
- 📊 统计分析
- 🔐 JWT 身份验证

## 技术栈

### 后端

- Go 1.21
- Gin Web 框架
- GORM ORM
- SQLite 数据库
- JWT 认证

### 前端

- Vue.js 3
- Vite 构建工具
- 现代化响应式 UI

## Docker 部署

### 快速启动

```bash
docker run -d -p 8082:8082 --name Central-Storage-System yht0511/central-storage-system:latest
```

### Docker Compose

## 环境变量

| 变量名  | 描述       | 默认值              |
| ------- | ---------- | ------------------- |
| PORT    | 服务端口   | 8082                |
| DB_PATH | 数据库路径 | ./data/storage_system.db |

## API 端点

- `GET /api/health` - 健康检查
- `POST /api/auth/login` - 用户登录
- `GET /api/laboratories` - 获取实验室列表
- `GET /api/items` - 获取物品列表
- `GET /api/movements` - 获取移动历史

## 开发

### 本地开发环境

1. 克隆仓库

```bash
git clone https://github.com/yht0511/central-storage-system.git
cd central-storage-system
```

2. 启动后端

```bash
cd GO
go mod download
go run main.go
```

3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 构建 Docker 镜像

```bash
docker build -t central-storage-system .
```

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

如果您遇到任何问题，请在 GitHub 上创建 Issue。
