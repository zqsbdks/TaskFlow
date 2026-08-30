"""顶层 API 路由聚合模块。

每个业务模块应拥有自己的 ``APIRouter``，再通过 ``api_router.include_router``
挂载到这里。应用工厂只需要包含该聚合路由即可。
"""

from fastapi import APIRouter

from app.routers.tag import tag_router
from app.routers.task import task_router
from app.routers.user import user_router
from app.routers.admin_user import admin_user_router

# 标签路由器

# api_router：汇总各业务路由的顶层路由器，最终在 app.main 中添加 /api/v1 前缀。
api_router = APIRouter()

# 将用户路由纳入顶层聚合路由；main.py 会统一添加 API 版本前缀。
api_router.include_router(user_router)
# 将任务路由纳入顶层聚合路由，最终路径以 /api/v1/tasks 开头。
api_router.include_router(task_router)
# 将标签路由纳入顶层聚合路由，最终路径以 /api/v1/tags 开头。
api_router.include_router(tag_router)
# 将管理员用户路由纳入顶层聚合路由，最终路径以 /api/v1/admin/user 开头。
api_router.include_router(admin_user_router)

__all__ = ["api_router"]
