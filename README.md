# QQ三国工具 (QQSG Tool)

一个基于 FastAPI + Vue 3 的 QQ三国 物品/配方查询工具。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy + Alembic |
| 前端 | Vue 3 + Vite + Element Plus + Pinia |
| 数据库 | MySQL 5.7 |
| 部署 | Docker Compose |

## 项目结构

```
qqsg-tool/
├── backend/                 # 后端 (FastAPI)
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── core/            # 核心配置、安全、数据同步
│   │   └── models/          # ORM 模型
│   ├── alembic/             # 数据库迁移
│   ├── Dockerfile
│   ├── docker-entrypoint.sh
│   └── requirements.txt
├── frontend/                # 前端 (Vue 3)
│   ├── src/
│   │   ├── api/             # API 请求封装
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   └── views/           # 页面组件
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── sql/
│   ├── init/                # 建表 SQL（首次初始化执行）
│   └── data/                # 数据 SQL（每次启动同步）
├── docker-compose.yml
└── README.md               # 项目说明文件
```

---

## 快速开始（Docker 部署）

**推荐方式**，无需手动配置 Python/Node 环境。

### 前置：配置 Docker 镜像加速（国内必做）

由于 `node:18-alpine` 和 `nginx:alpine` 等基础镜像需要从 Docker Hub 拉取，国内直接拉取可能很慢或卡住。请先配置镜像加速器：

**Docker Desktop（Windows/macOS）**：
打开 Settings → Docker Engine，在 `registry-mirrors` 中添加：
```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ]
}
```
然后点击 "Apply & Restart"。

**Linux**：编辑 `/etc/docker/daemon.json`，添加同上配置后执行 `sudo systemctl restart docker`。

### 构建启动

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

启动后访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:9939 | 用户界面 |
| API 文档 | http://localhost:9940/docs | Swagger UI |
| 健康检查 | http://localhost:9940/health | 后端状态 |

**数据库初始化说明**：
- 首次启动：后端自动检测 → 执行 `sql/init/` 建表 → Alembic 标记版本 → 导入 `sql/data/` 数据
- 后续启动：Alembic 自动迁移 + 数据同步（`INSERT IGNORE` 幂等执行）
- 修改 ORM 模型后：直接 `docker-compose up -d --build`，entrypoint 自动生成迁移并执行

---

## 本地开发

### 前置条件

- Python 3.11+
- Node.js 18+
- MySQL 5.7+

### 1. 配置环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env 修改数据库连接等信息
```

### 2. 安装后端依赖

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate

cd backend
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 初始化数据库

```bash
# 执行建表 SQL
mysql -u root -p qqsg < sql/init/00_init.sql

# 导入初始数据
mysql -u root -p qqsg < sql/data/items.sql
mysql -u root -p qqsg < sql/data/recipes.sql
# ... 其他数据文件

# 标记 Alembic 版本
cd backend
alembic stamp head
```

### 4. 启动后端

```bash
cd backend
python run.py
```

后端运行在 http://localhost:9940，API 文档 http://localhost:9940/docs

### 5. 启动前端

打开新终端：

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:9939，Vite 支持热更新。

### 停止服务

在各个终端窗口中按 `Ctrl+C` 停止对应服务。

---

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:9939 | 用户界面 |
| API 文档 | http://localhost:9940/docs | Swagger UI |
| 健康检查 | http://localhost:9940/health | 后端状态 |

---

## 默认账号

管理员 用户名：admin 密码：admin123

普通用户 用户名：user 密码：user123

---

## 数据管理

### 目录约定

| 目录 | 用途 | 执行时机 |
|------|------|----------|
| `sql/init/` | 建表 DDL | 仅首次初始化 |
| `sql/data/` | 业务数据 (INSERT) | 每次启动同步 |

### 添加新数据

1. 在 `sql/data/` 下新建 `.sql` 文件
2. 写入 `INSERT INTO` 语句
3. 重启容器即可自动同步（`INSERT IGNORE` 保证幂等）

### 修改表结构

1. 修改 `backend/app/models/` 中的 ORM 模型
2. `docker-compose up -d --build`
3. entrypoint 自动 `alembic revision --autogenerate` + `alembic upgrade head`

---

## 调试技巧

### 后端

- 后端终端显示所有 HTTP 请求和数据库查询
- 访问 http://localhost:9940/docs 直接测试 API
- Docker 模式：`docker-compose logs -f backend` 查看日志

### 前端

- Vite 热更新自动刷新页面
- 浏览器控制台查看 JavaScript 错误
- 推荐使用 Vue DevTools 浏览器插件
