# 阶段1：构建前端
FROM node:18-alpine AS build

WORKDIR /app

# 复制依赖文件并安装
COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com && npm ci

# 复制前端代码并构建
COPY . .
RUN npm run build

# 阶段2：使用 Nginx 提供静态文件服务
FROM nginx:alpine

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
