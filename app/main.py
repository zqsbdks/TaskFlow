"""FastAPI 应用主入口模块。

本模块负责创建应用实例、注册全局中间件、挂载业务路由，并提供一个简单的根路径接口，
用于确认服务是否成功启动。
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.logging import configure_logging
from app.core.middlewares import register_middlewares
from app.routers import api_router
from app.schemas import ResponseModel

# frontend_dir：项目自带的零构建前端目录，由 FastAPI 直接托管。
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"


def create_app() -> FastAPI:
    """创建并配置一个彼此独立的 FastAPI 应用实例。

    使用工厂函数而不是只在模块顶层拼装应用，既方便 Uvicorn 加载全局 ``app``，
    也允许测试代码为每个用例创建全新的应用，避免路由和中间件状态相互污染。

    Returns:
        FastAPI: 已配置日志、中间件、异常处理、生命周期和业务路由的应用。
    """

    # 日志必须在其他运行期组件开始记录消息前完成配置。
    configure_logging()

    # application：本次工厂调用创建的 FastAPI 实例，测试之间不会共享路由状态。
    # lifespan 统一接管数据库连接池等资源的启动与释放。
    application = FastAPI(
        title=settings.project_name,
        version=settings.project_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # 注册顺序集中放在应用工厂中，后续增加中间件或异常处理器时容易审查。
    register_middlewares(application)
    register_exception_handlers(application)

    # 静态资源使用独立路径，避免与 /api/v1 下的业务接口发生冲突。
    application.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    # 所有业务路由统一带上版本前缀，例如 /api/v1/users。
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.get("/app", include_in_schema=False)
    async def frontend_app() -> FileResponse:
        """返回项目内置的任务管理前端页面。"""

        return FileResponse(frontend_dir / "index.html")

    @application.get("/", response_model=ResponseModel[dict[str, str]])
    async def read_root() -> ResponseModel[dict[str, str]]:
        """返回基础欢迎信息，用于人工确认服务已经启动。"""

        return ResponseModel(data={"message": "Hello World"})

    @application.get("/health", response_model=ResponseModel[dict[str, str]])
    async def health() -> ResponseModel[dict[str, str]]:
        """提供不依赖外部服务的轻量存活检查。"""

        return ResponseModel(data={"status": "ok"})

    return application


# Uvicorn 默认通过 ``app.main:app`` 导入此全局 ASGI 对象。
app = create_app()

# 运行服务命令：uvicorn app.main:app --reload
