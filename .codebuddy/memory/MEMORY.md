# QQSG-Tool 项目记忆

## 项目概述
QQ三国工具 - 前后端分离的 Web 应用，FastAPI 后端 + Vue3 前端 + MySQL 5.7 数据库。

## 技术栈
- 后端：Python 3.11, FastAPI 0.109, SQLAlchemy 2.0, Uvicorn 0.27, 端口 9940
- 前端：Vue 3.4, Vite 5, Element Plus 2.5, Pinia, 端口 9939（生产用 Nginx:80）
- 数据库：MySQL 5.7, 库名 qqsg

## Docker 化 (2025-07-19)
- 使用 docker-compose 编排 mysql + backend + frontend 三个服务
- **数据库生命周期完全由 Python 后端管理**（`data_sync.py`），MySQL 容器只负责存储
- 首次启动：后端检测无 users 表 → 执行 `sql/init/00_init.sql` 建表 → `alembic stamp head` 标记版本 → 导入 `sql/data/` 数据
- 后续启动：检测已有 users 表 → Alembic 自动迁移 + 数据同步
- 不再使用 MySQL 的 `docker-entrypoint-initdb.d`，避免两套初始化流程
- 配置了 Alembic 数据库迁移，**全自动**：修改模型后直接 `docker-compose up -d --build`
- 前端独立构建（Node 构建 + Nginx 运行），Nginx 代理 /api 到后端
- `backend/Dockerfile` 是纯 Python 后端构建（不含前端），前后端各自独立 Dockerfile

## 目录结构约定
- `sql/init/` — 建表 SQL（仅首次初始化执行），如 `00_init.sql`
- `sql/data/` — 数据 SQL（每次启动同步，INSERT IGNORE 幂等），如 `items.sql`、`recipes.sql` 等

## 数据库变更策略
- **表结构变更**：修改 `backend/app/models/` 模型 → `docker-compose up -d --build`，Alembic 自动生成并执行迁移
- **数据变更**（INSERT/UPDATE/DELETE）：编辑 `sql/data/` 下对应 `.sql` 文件，每次启动自动执行
- 如需完全重建：`docker-compose down -v && docker-compose up -d --build`（会丢失运行时数据）
```bash
docker-compose up -d --build   # 构建并启动
docker-compose down            # 停止
```
访问：前端 http://localhost:9939，后端 http://localhost:9940

## 数据卷
- mysql_data: 持久化 MySQL 数据，容器重启不丢失
