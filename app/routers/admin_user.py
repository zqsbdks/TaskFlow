"""管理员用户 API 路由。"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.schemas.admin_user_request import AdminUserListRequest
from app.schemas.admin_user_response import AdminUserListResponse
from app.schemas.base import ResponseModel
from app.services.admin_user import get_user_lists_service

admin_user_router = APIRouter(prefix="/admin/user", tags=["管理员用户"])


@admin_user_router.get(
    "/list",
    response_model=ResponseModel[AdminUserListResponse],
)
async def get_user_lists(
    query: Annotated[AdminUserListRequest, Query()],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页获取用户，仅允许已启用的管理员访问。"""

    # GET 查询参数由 AdminUserListRequest 校验，权限和分页计算交给 Service。
    user_list = await get_user_lists_service(
        db=db,
        current_user=current_user,
        query=query,
    )

    # response_model 会把 items 中的 User ORM 对象转换成公开的用户响应字段。
    return ResponseModel(
        message="获取用户列表成功",
        data=user_list,
    )


__all__ = ["admin_user_router"]
