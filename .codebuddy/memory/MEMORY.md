# QQSG-Tool 项目记忆

## 项目概述
QQ三国工具 - 前后端分离的 Web 应用，FastAPI 后端 + Vue3 前端 + MySQL 5.7 数据库。

## 技术栈
- 后端：Python 3.11, FastAPI 0.109, SQLAlchemy 2.0, Uvicorn 0.27, 端口 9940
- 前端：Vue 3.4, Vite 5, Element Plus 2.5, Pinia, 端口 9939（生产用 Nginx:80）
- 数据库：MySQL 5.7, 库名 qqsg

## Docker 化 (2025-07-19)
- 使用 docker-compose 编排 mysql + backend + frontend 三个服务
- SQL 文件 `sql/qqsg.sql` 在 MySQL 首次初始化时自动执行（含表结构 + 初始数据）
- 配置了 Alembic 数据库迁移，**全自动**：修改模型后直接 `docker-compose up -d --build`，entrypoint 自动 `revision --autogenerate` + `upgrade head`
- 移除了 `main.py` 中的 `create_all`，表结构完全由 Alembic 管理
- `sql/qqsg.sql` 包含 `item_tags` 表（不在 ORM 模型中），autogenerate 不会删除该表
- 前端使用多阶段构建（Node 构建 + Nginx 运行），Nginx 代理 /api 到后端

## 数据库变更策略
- Alembic 自动管理**表结构**变更，改模型后直接 `docker-compose up -d --build`
- **数据变更**（INSERT/UPDATE）需在迁移文件中手写 `op.execute("SQL")`，或生成空迁移 `alembic revision -m "描述"`
- `sql/qqsg.sql` 仅作为初始数据快照，仅在 MySQL 首次初始化时执行
- 如需完全重建数据：`docker-compose down -v && docker-compose up -d --build`（会丢失运行时数据）
```bash
docker-compose up -d --build   # 构建并启动
docker-compose down            # 停止
```
访问：前端 http://localhost:9939，后端 http://localhost:9940

## 数据卷
- mysql_data: 持久化 MySQL 数据，容器重启不丢失
