# 第一阶段：构建前端
FROM node:18-alpine AS frontend-builder

# 设置工作目录
WORKDIR /app/frontend

# 复制前端package.json和package-lock.json
COPY frontend/package*.json ./

# 安装前端依赖
RUN npm install

# 复制前端源代码
COPY frontend/ ./

# 构建前端应用
RUN npm run build

# 第二阶段：构建后端
FROM --platform=$BUILDPLATFORM golang:1.21-bullseye AS backend-builder

# 声明构建参数
ARG TARGETOS
ARG TARGETARCH

# 安装必要的包
RUN apt-get update && apt-get install -y \
    gcc \
    libc6-dev \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app/backend

# 复制go.mod和go.sum文件
COPY GO/go.mod GO/go.sum ./

# 下载依赖
RUN go mod download

# 复制后端源代码
COPY GO/ ./

# 设置构建参数
ENV CGO_ENABLED=1
ENV GOOS=$TARGETOS
ENV GOARCH=$TARGETARCH

# 构建应用
RUN go build -a -ldflags '-linkmode external -extldflags "-static"' -o main .

# 第三阶段：最终运行环境
FROM alpine:latest

# 安装ca-certificates和sqlite
RUN apk --no-cache add ca-certificates sqlite

# 创建Program目录
RUN mkdir -p /Program

# 设置工作目录
WORKDIR /Program

# 从前端构建阶段复制dist文件夹
COPY --from=frontend-builder /app/frontend/dist ./dist

# 从后端构建阶段复制可执行文件
COPY --from=backend-builder /app/backend/main ./main

# 暴露端口
EXPOSE 8082

# 运行应用
CMD ["./main"]
