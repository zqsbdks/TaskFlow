# TaskFlow

TaskFlow 是一个前后端一体的异步任务管理系统，当前版本为 `1.0.0`。项目使用
FastAPI 提供 API 和静态前端，支持用户认证、任务管理、标签关联及管理员功能，
适合用于学习完整的 Router → Service → CRUD 分层和部署流程。

## 功能

- 用户注册、登录、JWT Bearer 身份认证
- 查看和修改个人资料、修改密码
- 创建、分页筛选、更新、删除任务
- 独立更新任务状态并自动维护完成时间
- 创建标签、查看标签、为任务添加或移除标签
- 管理员分页查看、启用、禁用和删除用户
- 管理员分页查看所有用户的任务
- 统一的 `code`、`message`、`data` API 响应结构
- 响应式任务管理前端，兼容桌面端和移动端
- Alembic 数据库迁移、Ruff、MyPy 和 pytest 质量检查

## 技术栈

| 分类 | 技术 |
|---|---|
| Web API | FastAPI、Uvicorn |
| 数据验证 | Pydantic v2、pydantic-settings |
| 数据库 | MySQL、SQLAlchemy 2.x Async、aiomysql |
| 数据迁移 | Alembic |
| 认证安全 | JWT、Passlib、Argon2 |
| 前端 | 原生 HTML、CSS、JavaScript |
| 测试与质量 | pytest、Ruff、MyPy |

项目当前没有使用 Redis、服务端缓存、Jinja2 模板或 Node.js 构建工具。

## 快速开始

### 1. 克隆并初始化

```powershell
git clone <your-repository-url>
cd TaskFlow
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

初始化脚本会创建 `.venv`、从 `.env.example` 生成 `.env`、生成随机 JWT 密钥并安装依赖。
如果 `.env` 已存在，脚本不会覆盖原配置。

也可以在 VS Code 中按 `Ctrl+Shift+P`，选择 `Tasks: Run Task`，然后运行：

```text
Setup: 克隆后初始化项目
```

### 2. 配置 MySQL

编辑不会被 Git 提交的 `.env`：

```dotenv
APP_PROJECT_NAME="TaskFlow"
APP_PROJECT_VERSION="1.0.0"
APP_DATABASE_URL="mysql+aiomysql://user:password@localhost:3306/taskflow?charset=utf8mb4"
APP_SECRET_KEY="本地初始化脚本生成的随机密钥"
```

### 3. 创建数据库表

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Alembic 只迁移表结构，不会复制其他数据库的数据，也不会自动创建管理员。

### 4. 启动项目

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

启动后可以访问：

| 地址 | 作用 |
|---|---|
| `http://127.0.0.1:8000/app` | TaskFlow 前端 |
| `http://127.0.0.1:8000/docs` | Swagger API 文档 |
| `http://127.0.0.1:8000/openapi.json` | OpenAPI 文档 |
| `http://127.0.0.1:8000/health` | 存活检查 |

前端和 API 由同一个 FastAPI 服务提供。前端使用相对地址 `/api/v1`，因此不需要单独的
前端 `.env`，部署到不同域名时也不需要修改 JavaScript 中的服务器地址。

## 项目结构

```text
TaskFlow/
├── app/
│   ├── core/          # 配置、数据库、JWT、安全、异常和生命周期
│   ├── crud/          # SQLAlchemy 查询与数据库写入
│   ├── dependencies/  # 数据库会话和当前用户依赖
│   ├── models/        # User、Task、Tag、TaskTag ORM 模型
│   ├── routers/       # 用户、任务、标签和管理员 API
│   ├── schemas/       # Pydantic 请求与响应模型
│   ├── services/      # 权限检查和业务流程
│   └── main.py        # FastAPI 应用工厂、路由及前端挂载入口
├── frontend/
│   ├── index.html     # 单页前端结构
│   ├── styles.css     # 响应式页面样式
│   └── app.js         # API 调用和页面交互
├── alembic/           # 数据库迁移环境与版本脚本
├── scripts/           # 初始化与依赖快照脚本
├── tests/             # 单元测试和可选 MySQL 集成测试
├── .env.example       # 本地环境变量模板
└── .env.production.example  # Linux 生产环境模板
```

每增加一个 ORM 模型，都需要在 `app/models/__init__.py` 中导入，确保 Alembic 能发现。
每增加一个业务路由，都需要在 `app/routers/__init__.py` 中挂载到 `api_router`。

## 主要 API

所有业务接口统一使用 `/api/v1` 前缀。

| 模块 | 接口示例 |
|---|---|
| 用户 | `/users/register`、`/users/login`、`/users/info` |
| 任务 | `/tasks/create`、`/tasks/list`、`/tasks/detail/{task_id}` |
| 标签 | `/tags/create`、`/tags/list`、`/tags/task/{task_id}/tag/{tag_id}` |
| 管理员 | `/admin/user/list`、`/admin/user/task/list` |

需要认证的接口必须发送：

```http
Authorization: Bearer <access_token>
```

## 管理员账户

项目当前不会在应用启动或 Alembic 迁移时自动创建管理员。首次部署可以先通过注册接口创建
普通用户，再在 MySQL 中将该用户角色改为管理员：

```sql
UPDATE `user`
SET `role` = 'admin'
WHERE `email` = 'admin@example.com';
```

不要在代码、迁移文件或 GitHub 仓库中保存固定管理员密码。

## 数据库迁移

```powershell
# 根据 ORM 模型生成迁移
python -m alembic revision --autogenerate -m "describe schema change"

# 升级到最新结构
python -m alembic upgrade head

# 回退一个迁移版本
python -m alembic downgrade -1
```

生成迁移后必须检查脚本内容，再应用到生产数据库。部署前应备份已有数据。

## Linux 部署

仓库提供 `.env.production.example` 作为生产配置模板：

```bash
git clone <your-repository-url>
cd TaskFlow

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

cp .env.production.example .env
nano .env

python -m alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

生产环境必须完成以下配置：

- 将 `APP_DEBUG` 和 `APP_DATABASE_ECHO` 设置为 `false`
- 使用 `openssl rand -hex 32` 生成独立的 `APP_SECRET_KEY`
- 配置生产 MySQL 地址并保证数据库数据使用持久化存储
- 使用 Nginx 提供 HTTPS 反向代理
- 使用 systemd、Supervisor 或容器平台保持 Uvicorn 进程运行
- 执行迁移前备份数据库

真实 `.env`、`.env.production`、虚拟环境和缓存目录均已被 `.gitignore` 排除，禁止将
数据库密码、JWT 密钥或管理员密码上传到 GitHub。

## 测试与代码质量

```powershell
python -m ruff format --check .
python -m ruff check .
python -m mypy app
python -m pytest
```

运行需要真实 MySQL 的集成测试：

```powershell
$env:RUN_MYSQL_TESTS="1"
python -m pytest -m integration
```

VS Code 中也可以运行 `Quality: 完整检查` 任务。更多命令见 [COMMANDS.md](COMMANDS.md)，
命名规则见 [NAMING.md](NAMING.md)。

## 版本

当前版本：`1.0.0`

应用版本通过 `APP_PROJECT_VERSION` 配置并显示在 Swagger/OpenAPI 中；API 路径版本
`/api/v1` 与应用发布版本相互独立。
