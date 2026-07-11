# 项目重构需求说明（最终版）

## 一、项目背景

当前项目技术栈：

### 前端

* Vue3
* Vite
* Vue Router
* Pinia

### 后端

* Python
* FastAPI

### 数据库

* MySQL

### 机器人

* AstrBot

### 部署方式

未来统一使用 Docker 部署：

* frontend
* backend
* mysql
* astrbot

---

# 二、当前项目目录

## Frontend

```text
src
├── api
├── assets
│   └── styles
├── components
│   ├── Header.vue
│   ├── Footer.vue
│   ├── ItemTreeDialog.vue
│   ├── RecipeCard.vue
│   └── RecipeFlow.vue
├── composables
├── router
├── stores
├── utils
└── views
    ├── admin
    ├── home
    ├── items
    ├── login
    ├── recipes
    └── register
```

## Backend

```text
app
├── api
│   ├── auth.py
│   ├── items.py
│   └── recipes.py
├── core
├── models
├── schemas
└── main.py
```

当前目录结构基本合理。

不要进行大规模目录重构。

只增加必要模块即可。

---

# 三、目前存在的问题

目前：

配方详情

采用：

RecipeDetailDialog.vue

进行弹窗展示。

例如：

```
配方列表

↓

点击详情

↓

Dialog弹窗
```

这种方式存在几个问题：

* 无法直接分享链接
* QQ机器人无法直接访问详情
* Playwright需要模拟点击弹窗
* 后续公网部署不方便
* URL无法唯一标识一个配方

因此决定：

取消详情弹窗。

改为独立详情页面。

---

# 四、重构目标

整个项目统一改为：

列表页

↓

点击

↓

独立详情页

例如：

```
/recipes

↓

/recipes/:id
```

或者：

```
/recipes/:recipeId
```

推荐采用 RESTful 风格。

---

# 五、前端改造

## Recipes

当前：

```
Recipes列表

↓

RecipeDetailDialog.vue
```

修改为：

```
Recipes列表

↓

router.push()

↓

RecipeDetail.vue
```

---

新增：

```
views

recipes

├── index.vue

├── detail.vue

├── components

│   ├── RecipeCard.vue

│   ├── RecipeFlow.vue

│   ├── MaterialTree.vue

│   └── RecipeEditDialog.vue
```

删除：

```
RecipeDetailDialog.vue
```

因为已经不需要。

---

## 路由修改

新增：

```
/recipes

/recipes/:id
```

例如：

```
/recipes/15
```

即可查看：

编号15的配方。

---

## RecipeDetail.vue

负责展示：

* 配方名称
* 配方图片
* 合成流程
* RecipeFlow
* MaterialTree
* 所需材料
* 合成结果
* 相关推荐（以后可扩展）

页面布局不要包含任何弹窗。

---

# 六、组件拆分原则

页面：

负责：

* 获取数据
* 调用API
* 页面布局

组件：

负责：

UI展示。

例如：

```
RecipeFlow.vue

MaterialTree.vue

RecipeCard.vue
```

继续保持组件化。

不要重新写第二套UI。

---

# 七、机器人分享方案

采用：

Playwright

截图详情页。

不再截图弹窗。

调用流程：

```
QQ群

↓

AstrBot

↓

Backend

↓

Playwright

↓

http://frontend/recipes/15

↓

截图

↓

返回PNG

↓

AstrBot发送QQ群
```

这样无需模拟点击。

实现最简单。

---

# 八、后端新增模块

新增：

```
app

services

└── render_service.py
```

负责：

* 启动Playwright
* 打开详情页
* 等待页面渲染完成
* 截图
* 返回PNG

不要把截图逻辑写进：

recipes.py

保持职责单一。

---

新增：

```
app/api

share.py
```

新增接口：

```
GET

/api/share/recipe/{id}
```

返回：

```
image/png
```

---

# 九、详情页截图要求

详情页需要支持截图。

因此：

页面不要依赖：

* 鼠标Hover
* 点击展开
* Dialog动画

进入页面后即可完整展示。

这样Playwright只需要：

```
page.goto()

↓

等待加载完成

↓

page.screenshot()
```

即可。

---

# 十、AstrBot职责

AstrBot只负责：

* 接收QQ群命令
* 调用接口
* 发送图片

不要：

* 查询数据库
* 拼HTML
* Playwright截图
* 查询业务逻辑

保持插件尽可能轻量。

---

# 十一、未来扩展

独立详情页以后可以直接支持：

```
https://domain.com/recipes/15
```

任何人都可以访问。

以后可增加：

* 分享链接
* 收藏
* 评论
* SEO
* Open Graph
* 分享卡片

机器人也无需修改。

---

# 十二、开发优先级

第一步：

修改：

RecipeDetailDialog

↓

RecipeDetail页面。

完成路由。

---

第二步：

修改：

列表页

点击详情

↓

router.push()

---

第三步：

新增：

```
views/recipes/detail.vue
```

完成详情展示。

---

第四步：

新增：

```
render_service.py
```

实现Playwright截图。

---

第五步：

新增：

```
GET

/api/share/recipe/{id}
```

返回PNG。

---

第六步：

AstrBot调用：

```
/api/share/recipe/{id}
```

发送QQ群。

---

# 十三、总体设计原则

整个项目遵循以下原则：

1. 一个配方只维护一套UI，不维护截图专用页面。

2. 前端负责展示，后端负责数据与图片生成。

3. AstrBot仅作为客户端，不承担业务逻辑。

4. 每个配方拥有唯一URL。

5. 使用详情页替代详情弹窗。

6. Playwright直接截图详情页，而不是模拟点击弹窗。

7. 保持当前目录结构，仅新增必要模块，不进行过度重构。

8. 代码优先考虑可维护性与后续扩展，而不是一次性实现。
