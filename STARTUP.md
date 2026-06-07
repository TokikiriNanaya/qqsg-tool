# 启动说明

## 📌 重要提示

**本项目使用虚拟环境（venv），请确保在激活虚拟环境后运行后端服务。**

---

## 🚀 启动步骤

### ⚠️ 前置条件

**在启动服务前，请确保：**

1. ✅ 已使用 SQL 文件创建所有数据库表
2. ✅ 已配置好 `.env` 文件中的数据库连接
3. ✅ 虚拟环境已激活

---

### 1️⃣ 启动后端服务

打开终端，激活虚拟环境：

```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

进入后端目录并启动：

```bash
cd backend
python run.py
```

✅ 后端运行在: http://localhost:9940
📚 API文档: http://localhost:9940/docs

💡 **保持此终端窗口开启**，可以看到实时日志，方便调试。

---

### 2️⃣ 启动前端服务

**打开新的终端窗口**（不要关闭后端窗口）：

```bash
cd frontend
npm run dev
```

✅ 前端运行在: http://localhost:9939

💡 **提示**:

- Vite支持热更新，修改代码后会自动刷新
- 前端终端会显示编译状态和错误信息
- **两个终端窗口都需要保持开启**

---

## 🛑 停止服务

在各个终端窗口中按 `Ctrl+C` 即可停止对应的服务。

---

## 🌐 访问地址

启动成功后，可以访问：


| 服务        | 地址                         | 说明       |
| ----------- | ---------------------------- | ---------- |
| 📱 前端界面 | http://localhost:9939        | 用户界面   |
| 📚 API文档  | http://localhost:9940/docs   | Swagger UI |
| 🔧 健康检查 | http://localhost:9940/health | 后端状态   |

---

## 🔑 默认账号

**注意：需要手动在数据库中创建管理员账户**

```sql
-- 示例：创建管理员账户（密码需要使用 bcrypt 加密）
INSERT INTO users (username, email, hashed_password, role, is_active) 
VALUES ('admin', 'admin@qqsg.com', '$2b$12$...', 'admin', TRUE);
```

或使用你的 SQL 迁移文件中的初始数据。

---

## 💡 调试技巧

### 后端调试

- 后端终端会显示所有HTTP请求和数据库查询
- 访问 http://localhost:9940/docs 可以直接测试API
- 在代码中添加 `print()` 或断点调试

### 前端调试

- 前端终端会显示编译警告和错误
- 浏览器控制台可以查看JavaScript错误
- Vite热更新会自动刷新页面
- 使用Vue DevTools浏览器插件调试组件

---
