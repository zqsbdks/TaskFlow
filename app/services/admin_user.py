"""管理员用户业务服务。"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.admin_user import get_user_list
from app.models.user import User
from app.schemas.admin_user_request import AdminUserListRequest
from app.schemas.admin_user_response import (
    AdminUserListItemResponse,
    AdminUserListResponse,
)


async def get_user_lists_service(
    db: AsyncSession,
    current_user: User,
    query: AdminUserListRequest,
) -> AdminUserListResponse:
    """校验管理员账号状态并分页返回用户。

    Args:
        db: 当前请求使用的异步数据库会话。
        current_user: 由访问令牌确定的当前登录用户。
        query: 已通过 Pydantic 校验的分页参数。

    Returns:
        当前页用户及其分页信息。

    Raises:
        HTTPException: 当前用户不是管理员或账号已被禁用时返回 HTTP 403。
    """

    # 只有管理员可以读取全站用户，普通用户不能通过该接口枚举账号。
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问",
        )

    # 禁用状态的管理员同样不能继续执行管理操作。
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # SQLAlchemy 的 offset 从 0 开始，因此需要根据当前页码换算偏移量。
    offset = (query.page - 1) * query.page_size
    users, total = await get_user_list(
        db=db,
        offset=offset,
        limit=query.page_size,
    )

    # 使用整数运算向上取整；没有用户时总页数为 0。
    total_pages = (total + query.page_size - 1) // query.page_size

    # 显式转换 ORM 对象，确保只返回允许公开的字段并满足静态类型检查。
    user_items = [AdminUserListItemResponse.model_validate(user) for user in users]

    return AdminUserListResponse(
        items=user_items,
        total=total,
        page=query.page,
        page_size=query.page_size,
        total_pages=total_pages,
    )


__all__ = ["get_user_lists_service"]
