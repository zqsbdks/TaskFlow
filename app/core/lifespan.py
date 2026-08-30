"""应用生命周期管理模块。

本模块定义 FastAPI 的生命周期上下文，并在应用关闭阶段释放数据库连接池，
避免开发热重载或服务停止后遗留数据库连接。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """在应用启动和关闭时管理资源生命周期。

    Args:
        app (FastAPI): 当前 FastAPI 应用实例。
    """
    # 即使当前函数未直接使用 app，保留该参数以符合 FastAPI lifespan 协议。
    _ = app

    # yield 之前是启动阶段，之后是应用收到关闭信号后的清理阶段。
    yield

    # 释放 SQLAlchemy Engine 持有的数据库连接池。
    await async_engine.dispose()
