# 食探社 — 华农校园美食分享平台

前后端分离架构：FastAPI + Tortoise-ORM（后端） / React + Vite + Tailwind CSS（前端）。

---

## 目录结构

```
FoodieHub/
├── backend/           # FastAPI 后端
│   ├── dao/           # 数据访问层
│   ├── models/        # Tortoise ORM 模型
│   ├── routers/       # API 路由
│   ├── schemas/       # Pydantic 数据模型
│   ├── services/      # 业务逻辑层
│   ├── utils/         # 工具函数（JWT、密码等）
│   ├── static/        # 静态文件（上传图片等）
│   ├── migrations/    # Aerich 数据库迁移
│   ├── config.py      # 配置
│   └── main.py        # 入口
├── frontend/          # React 前端
│   ├── src/
│   │   ├── admin/     # 管理后台页面
│   │   ├── api/       # API 请求封装
│   │   ├── components/# 通用组件
│   │   ├── pages/     # 页面组件
│   │   ├── store/     # Zustand 状态管理
│   │   └── types/     # TypeScript 类型定义
│   ├── vite.config.ts # Vite 配置
│   └── package.json
├── README.md
└── .gitignore
```

---

## 前端部署

### 前置依赖

- **Node.js** ≥ 18（推荐 20 LTS）
- **npm**（随 Node.js 一同安装）或 **pnpm**

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

默认在 `http://localhost:5173` 启动。

Vite 已配置代理（`vite.config.ts`）：
- `/api/*` → `http://127.0.0.1:8000/*`（去掉 `/api` 前缀）
- `/static/*` → `http://127.0.0.1:8000/static/*`

即前端开发时请求 `/api/users/login` 会自动转发到后端 `http://127.0.0.1:8000/users/login`。

### 3. 构建生产包

```bash
npm run build
```

产物输出到 `frontend/dist/`。

---

## 后端部署

### 前置依赖

- **Python** ≥ 3.10（推荐 3.11）
- **MySQL** ≥ 8.0

### 1. 创建虚拟环境

```bash
cd backend

# Windows
python -m venv env
.\env\Scripts\activate

# macOS / Linux
python3 -m venv env
source env/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

编辑 `.env` 文件，填入实际的数据库连接信息和密钥：

```ini
# 数据库连接（MySQL 8+）
DATABASE_URL=mysql://root:your_password@localhost:3306/foodiehub

# JWT 签名密钥（生产环境请使用长随机字符串）
JWT_SECRET_KEY=change-this-to-a-random-string

# 调试模式
DEBUG=true
```

### 4. 创建数据库

登录 MySQL 并创建数据库（如尚未创建）：

```sql
CREATE DATABASE foodiehub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 初始化数据库表

确保虚拟环境已激活，在 `backend/` 目录下执行：

```bash
# 首次：初始化 Aerich
PYTHONPATH=. python -m aerich init -t config.settings.TORTOISE_ORM

# 应用迁移
PYTHONPATH=. python -m aerich upgrade
```

> **注意**：如果已有迁移文件（`backend/migrations/`），直接执行 `aerich upgrade` 即可。
> 如果遇到 "Table 'aerich' already exists" 错误，说明已初始化过，可忽略。

### 6. 启动开发服务器

```bash
PYTHONPATH=. python -m uvicorn main:app --reload --port 8000
```

默认在 `http://localhost:8000` 启动。API 文档（Swagger UI）：`http://localhost:8000/docs`

---

## 日常开发流程

### 同时启动前后端

```bash
# 终端 1：后端
cd backend
.\env\Scripts\activate
PYTHONPATH=. python -m uvicorn main:app --reload --port 8000

# 终端 2：前端
cd frontend
npm run dev
```

浏览器访问 `http://localhost:5173`，前端通过 Vite proxy 调用后端 API。

### 数据库模型变更

```bash
# 修改 models/ 下的文件后，生成迁移
cd backend
.\env\Scripts\activate
PYTHONPATH=. python -m aerich migrate

# 应用迁移
PYTHONPATH=. python -m aerich upgrade
```

---

## 技术栈

| 层 | 技术 |
|---|---|
| 后端框架 | FastAPI |
| ORM | Tortoise-ORM |
| 数据库迁移 | Aerich |
| 认证 | JWT（python-jose） |
| 前端框架 | React 19 + Vite |
| 样式 | Tailwind CSS |
| 状态管理 | Zustand |
| 请求库 | Axios |
| 管理后台 | react-admin（MUI） |
| 图标 | lucide-react |
