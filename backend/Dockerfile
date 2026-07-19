# ============================================
# 阶段1：构建前端
# ============================================
FROM node:18-alpine AS frontend-build

WORKDIR /frontend

# 复制前端依赖文件并安装
COPY ../frontend/package*.json ./
RUN npm config set registry https://registry.npmmirror.com && npm ci

# 复制前端代码并构建
COPY ../frontend/ ./
RUN npm run build

# ============================================
# 阶段2：Python 后端 + 前端静态文件
# ============================================
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（mysqlclient 需要 gcc 和 libmariadb-dev）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制后端应用代码
COPY . .

# 复制前端构建产物到静态目录
COPY --from=frontend-build /frontend/dist /app/static

# 启动脚本（含数据库迁移）
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# 暴露端口
EXPOSE 9940

# 启动命令
ENTRYPOINT ["/docker-entrypoint.sh"]
