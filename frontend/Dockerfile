# 阶段1：构建前端
FROM docker.1ms.run/library/node:18-alpine AS build

WORKDIR /app

# 使用国内 npm 源
COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com \
    && npm ci

# 复制源码并构建
COPY . .
RUN npm run build

# 阶段2：使用 Nginx 提供静态文件
FROM docker.1ms.run/library/nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]