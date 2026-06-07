# QQ三国工具 - 配方查询系统

一个基于 Vue3 + FastAPI + MySQL 的MMO游戏配方查询与管理平台。

---

## 📋 目录

- [项目简介](#项目简介)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [数据库设计](#数据库设计)
- [API接口](#api接口)
- [开发指南](#开发指南)
- [常见问题](#常见问题)

---

## 项目简介

这是一个用于管理MMO游戏（QQ三国）中物品和配方的工具网站，主要功能包括：

### ✨ 核心功能

- **物品管理** - 维护游戏内所有物品信息
- **标签系统** - 灵活的标签分类（获取来源、用途等）
- **配方管理** - 记录物品制作配方和所需材料
- **权限控制** - 管理员和普通用户两种角色
- **配方查询** - 快速搜索和浏览配方信息

### 👥 用户角色

| 角色 | 权限 |
|------|------|
| **普通用户** | 查看所有物品和配方、创建新配方 |
| **管理员** | 所有权限 + 编辑/删除物品、配方、标签 |

---

## 技术栈

### 后端
- **框架**: FastAPI 0.109+
- **数据库**: MySQL 5.7+
- **ORM**: SQLAlchemy 2.0+
- **认证**: JWT (python-jose)
- **密码加密**: Bcrypt (passlib)

### 前端
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite 5+
- **UI组件**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios

---

## 快速开始

#### 前置要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+
- **推荐使用虚拟环境（venv）**

#### 1. 创建数据库

```sql
CREATE DATABASE qqsg CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 2. 配置后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
Copy-Item .env.example .env
# 编辑 .env 文件，修改数据库密码
```

在 `.env` 文件中配置：
```env
DATABASE_URL = "mysql+pymysql://root:你的密码@localhost:3306/qqsg?charset=utf8mb4"
SECRET_KEY = "生成一个随机字符串"
```

#### 3. 手动创建数据库表

**重要：需要手动创建所有数据库表**

请使用你现有的 SQL 文件执行一键迁移，或参考 `backend/DATABASE_SCHEMA.md` 手动创建以下表：
- `users` - 用户表
- `tags` - 标签表
- `item_tags` - 物品-标签关联表
- `items` - 物品表
- `recipes` - 配方表

#### 4. 启动后端服务

**重要：请在激活虚拟环境后运行**

```bash
# 激活虚拟环境（如果还未激活）
# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate

# 启动后端
cd backend
python run.py
```

后端运行在: http://localhost:9940  
API文档: http://localhost:9940/docs

💡 **提示**: 保持此终端窗口开启，可以看到实时日志，方便调试。

#### 5. 启动前端服务

**打开新的终端窗口**（不要关闭后端窗口）：

```bash
cd frontend

# 首次运行需要安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在: http://localhost:5173

💡 **提示**: 
- Vite支持热更新，修改代码后会自动刷新
- 前端终端会显示编译状态和错误信息
- 两个终端窗口都需要保持开启

---

## 项目结构

```
qqsg-tool/
│
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   ├── auth.py       # 认证接口
│   │   │   ├── items.py      # 物品接口
│   │   │   └── recipes.py    # 配方接口
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py     # 应用配置
│   │   │   ├── database.py   # 数据库连接
│   │   │   └── security.py   # JWT认证
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic模式
│   │   └── main.py           # 应用入口
│   ├── requirements.txt       # Python依赖
│   ├── .env.example          # 环境变量示例
│   ├── test_db.py            # 测试数据库
│   └── run.py                # 启动脚本
│
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── api/              # API调用
│   │   ├── components/       # 公共组件
│   │   ├── router/           # 路由配置
│   │   ├── stores/           # 状态管理
│   │   ├── utils/            # 工具函数
│   │   ├── views/            # 页面视图
│   │   ├── App.vue           # 根组件
│   │   └── main.js           # 入口文件
│   ├── package.json          # Node依赖
│   ├── vite.config.js        # Vite配置
│   └── index.html            # HTML模板
│
└── README.md                 # 本文档
```

---

## 数据库设计

### 核心表结构

#### 1. items (物品表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| name | VARCHAR(100) | 物品名称 |
| game_id | VARCHAR(50) | 游戏内ID（唯一） |
| description | TEXT | 物品简介 |
| bag_limit | INT | 背包上限（默认99） |
| warehouse_limit | INT | 仓库上限（默认999） |

#### 2. tags (标签表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| name | VARCHAR(50) | 标签名称（唯一） |
| category | VARCHAR(50) | 标签分类 |
| description | TEXT | 标签描述 |

**预设标签：**
- 获取来源：怪物掉落、任务奖励、商店购买、副本掉落、活动奖励、采集获得、制作获得
- 用途：制作材料、任务物品、装备强化、药品恢复、兑换道具、宠物培养、技能升级

#### 3. item_tags (物品-标签关联表)

多对多关系，一个物品可以有多个标签。

#### 4. recipes (配方表)

对应 MixData.txt 数据，包含以下主要字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键（序号） |
| name | VARCHAR(200) | 配方名称 |
| description | TEXT | 简介 |
| level_required | INT | 制作所需等级 |
| material1_id, material2_id, material3_id | INT | 材料ID |
| material1_quantity, ... | INT | 材料数量 |
| result_item_id | INT | 产出物品ID |
| result_quantity | INT | 产出数量 |
| lucky_probability | INT | 幸运合成概率 |
| lucky_result_item_id | INT | 幸运产出物品ID |
| profession_type | INT | 副职类型 |
| vitality_cost | INT | 消耗活力 |

详细字段定义请参考 `backend/app/models/__init__.py` 中的 Recipe 模型。

#### 5. users (用户表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| username | VARCHAR(50) | 用户名（唯一） |
| email | VARCHAR(100) | 邮箱（唯一） |
| hashed_password | VARCHAR(255) | 密码哈希 |
| role | ENUM | 角色（admin/user） |
| is_active | BOOLEAN | 是否活跃 |

---

## API接口

### 认证接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | 公开 |
| POST | `/api/auth/login` | 用户登录 | 公开 |

### 物品接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/items/` | 获取物品列表 | 公开 |
| GET | `/api/items/{id}` | 获取物品详情 | 公开 |
| POST | `/api/items/` | 创建物品 | 管理员 |
| PUT | `/api/items/{id}` | 更新物品 | 管理员 |
| DELETE | `/api/items/{id}` | 删除物品 | 管理员 |
| GET | `/api/items/tags/all` | 获取所有标签 | 公开 |
| POST | `/api/items/tags/` | 创建标签 | 管理员 |

### 配方接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/recipes/` | 获取配方列表 | 公开 |
| GET | `/api/recipes/{id}` | 获取配方详情 | 公开 |
| POST | `/api/recipes/` | 创建配方 | 登录用户 |
| PUT | `/api/recipes/{id}` | 更新配方 | 管理员 |
| DELETE | `/api/recipes/{id}` | 删除配方 | 管理员 |

### 请求示例

#### 创建物品

```json
POST /api/items/
{
  "name": "铁剑",
  "game_id": "ITEM_SWORD_001",
  "description": "一把普通的铁剑",
  "bag_limit": 50,
  "warehouse_limit": 500,
  "tag_ids": [1, 8]
}
```

#### 创建配方

```json
POST /api/recipes/
{
  "name": "铁剑锻造",
  "category": "武器",
  "level_required": 10,
  "result_item_id": 1,
  "materials": [
    {"item_id": 10, "quantity": 5},
    {"item_id": 11, "quantity": 2}
  ]
}
```

---

## 开发指南

### 添加新功能

#### 1. 后端开发流程

```bash
# 1. 在 models/__init__.py 中添加数据模型
# 2. 在 schemas/__init__.py 中添加Pydantic模式
# 3. 在 api/ 目录下创建路由文件
# 4. 在 main.py 中注册路由
```

#### 2. 前端开发流程

```bash
# 1. 在 views/ 下创建页面组件
# 2. 在 router/index.js 中添加路由
# 3. 在 api/ 下添加API调用函数
# 4. 在 stores/ 中添加状态管理（如需要）
```

### 代码规范

- **后端**: 遵循PEP 8规范
- **前端**: 使用Vue 3 Composition API
- **注释**: 所有函数添加文档字符串
- **命名**: 
  - Python: snake_case
  - JavaScript: camelCase
  - 数据库: snake_case

### 调试技巧

#### 后端调试

```python
# 在代码中添加
import pdb; pdb.set_trace()

# 或使用print
print(variable_name)
```

查看日志：
- 后端窗口显示实时日志
- 访问 http://localhost:9940/docs 测试API

#### 前端调试

```javascript
// 使用console.log
console.log('Debug:', data)

// 使用Vue DevTools浏览器插件
```

---

## 常见问题

### Q1: 如何停止服务？

在各个终端窗口中按 `Ctrl+C` 即可停止对应的服务。

- 后端窗口: 停止 FastAPI 服务
- 前端窗口: 停止 Vite 服务

### Q2: 数据库连接失败？

检查：
1. MySQL服务是否启动
2. `.env` 中的数据库配置是否正确
3. 数据库 `qqsg` 是否已创建
4. 用户名和密码是否正确

### Q3: 忘记管理员密码？

重置管理员密码：
```bash
cd backend
python
```

```python
from app.core.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.username == "admin").first()
user.hashed_password = get_password_hash("new_password")
db.commit()
```

### Q4: 前端无法连接后端？

检查：
1. 后端是否正常运行（访问 http://localhost:9940/health）
2. `frontend/vite.config.js` 中的代理配置
3. 浏览器控制台是否有CORS错误

### Q5: 如何激活虚拟环境？

**Windows:**
```powershell
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

激活后，终端前面会显示 `(.venv)` 标识。

### Q6: 如何批量导入物品数据？

可以编写Python脚本读取Excel/CSV：

```python
import pandas as pd
from app.core.database import SessionLocal
from app.models import Item

df = pd.read_excel('items.xlsx')
db = SessionLocal()

for _, row in df.iterrows():
    item = Item(
        name=row['name'],
        game_id=row['game_id'],
        description=row.get('description'),
        bag_limit=row.get('bag_limit', 99),
        warehouse_limit=row.get('warehouse_limit', 999)
    )
    db.add(item)

db.commit()
```

---

## 默认账号

```
管理员账号: admin
密码:       admin123
```

⚠️ **首次登录后请立即修改密码！**

---

## 下一步计划

- [ ] 配方收藏功能
- [ ] 用户评论系统
- [ ] 配方评分和排行
- [ ] 材料价格追踪
- [ ] 配方导入/导出
- [ ] 移动端适配优化
- [ ] 数据统计和分析

---

## 许可证

MIT License

---

## 联系方式

如有问题或建议，请提Issue或联系开发者。
