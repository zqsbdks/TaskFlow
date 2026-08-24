# 项目命令手册

本文集中记录项目初始化、开发、测试、数据库迁移和依赖管理命令。以下命令都应在
项目根目录执行。

## 1. 克隆后首次初始化

推荐在 VS Code 中按 `Ctrl+Shift+P`，选择 `Tasks: Run Task`，再选择：

```text
Setup: 克隆后初始化项目
```

该任务会依次完成：

1. 从 `.env.example` 创建 `.env`，已存在时不会覆盖。
2. 创建项目专用的 `.venv` 虚拟环境，已存在时不会重复创建。
3. 为新建的 `.env` 自动生成随机 `APP_SECRET_KEY`。
4. 升级虚拟环境中的 pip。
5. 安装 `requirements-dev.txt`，其中已经包含 `requirements.txt` 的运行依赖。
6. 执行 `pip check` 检查依赖冲突。

也可以在 PowerShell 中直接执行同一个脚本：

```powershell
.\scripts\setup.ps1
```

如果 PowerShell 阻止执行本地脚本，可以仅为本次命令放行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

初始化完成后，还需要修改 `.env` 中的项目名称和 MySQL 连接信息，并在 VS Code
中选择 `.venv\Scripts\python.exe` 解释器。

手动初始化时，等价命令如下：

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## 2. 虚拟环境

如果没有使用初始化任务，可以手动创建虚拟环境：

```cmd
python -m venv .venv
```

CMD 激活命令：

```cmd
.venv\Scripts\activate.bat
```

PowerShell 激活命令：

```powershell
.\.venv\Scripts\Activate.ps1
```

确认正在使用项目解释器：

```cmd
python -c "import sys; print(sys.executable)"
```

输出路径应以 `.venv\Scripts\python.exe` 结尾。

## 3. 安装依赖

只安装生产运行依赖：

```cmd
python -m pip install -r requirements.txt
```

安装生产依赖以及 pytest、Ruff、MyPy 等开发工具：

```cmd
python -m pip install -r requirements-dev.txt
```

检查当前环境是否存在依赖冲突：

```cmd
python -m pip check
```

## 4. 启动 FastAPI

启动带热重载的本地开发服务：

```cmd
python -m uvicorn app.main:app --reload
```

接口文档：`http://127.0.0.1:8000/docs`

健康检查：`http://127.0.0.1:8000/health`

按 `Ctrl+C` 停止服务。

## 5. 自动化测试

运行全部普通测试：

```cmd
python -m pytest
```

显示每个测试名称：

```cmd
python -m pytest -v
```

只重跑上次失败的测试：

```cmd
python -m pytest --lf
```

运行真实 MySQL 集成测试（CMD）：

```cmd
set RUN_MYSQL_TESTS=1
python -m pytest -m integration
set RUN_MYSQL_TESTS=
```

运行真实 MySQL 集成测试（PowerShell）：

```powershell
$env:RUN_MYSQL_TESTS="1"
python -m pytest -m integration
Remove-Item Env:RUN_MYSQL_TESTS
```

## 6. 代码质量

检查代码规范：

```cmd
python -m ruff check .
```

自动修复可以安全修复的规范问题：

```cmd
python -m ruff check . --fix
```

格式化代码：

```cmd
python -m ruff format .
```

检查类型标注：

```cmd
python -m mypy app
```

提交代码前建议依次运行：

```cmd
python -m ruff check .
python -m ruff format --check .
python -m mypy app
python -m pytest
```

## 7. Alembic 数据库迁移

根据 ORM 模型生成迁移：

```cmd
python -m alembic revision --autogenerate -m "迁移说明"
```

执行全部待处理迁移：

```cmd
python -m alembic upgrade head
```

回退一个版本：

```cmd
python -m alembic downgrade -1
```

查看当前版本和迁移历史：

```cmd
python -m alembic current
python -m alembic history
```

检查 ORM 模型是否存在尚未生成的结构变化：

```cmd
python -m alembic check
```

## 8. 生成依赖快照

推荐先生成临时快照，不直接覆盖手工维护的生产依赖：

```cmd
python scripts/freeze_requirements.py
```

脚本会使用当前 Python 解释器执行 `pip freeze`，并在根目录生成
`requirements-freeze.txt`。确认内容后，可以再让 AI 将其整理为生产依赖和开发依赖。

如果明确需要直接覆盖现有生产依赖，也可以手动执行：

```cmd
python -m pip freeze > requirements.txt
```

该命令会覆盖原文件，执行前应确认已经激活本项目 `.venv`。

## 9. VS Code 一键任务

按 `Ctrl+Shift+P`，选择 `Tasks: Run Task`，可以运行：

- `Setup: 克隆后初始化项目`
- `FastAPI: 启动开发服务`
- `Test: 运行普通测试`
- `Test: 运行 MySQL 集成测试`
- `Quality: Ruff 检查`
- `Quality: Ruff 格式检查`
- `Quality: MyPy 类型检查`
- `Quality: 完整检查`
- `Alembic: 生成迁移`
- `Alembic: 升级到 head`
- `Dependencies: 生成 freeze 快照`

其中生成迁移任务会在运行前提示输入迁移说明。
