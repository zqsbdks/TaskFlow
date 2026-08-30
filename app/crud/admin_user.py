"""管理员用户数据访问模块。

本模块只负责用户表查询，不处理权限判断或 HTTP 响应。
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.admin_user_request import AdminUpdateRequest


# region 管理员用户列表查询
async def get_user_list(
    db: AsyncSession,
    offset: int,
    limit: int,
) -> tuple[list[User], int]:
    """分页查询全部用户，并返回用户总数。"""

    # 数量查询不带分页条件，用于计算前端分页所需的总条数。
    count_statement = select(func.count(User.id))
    count_result = await db.scalar(count_statement)
    total = count_result if count_result is not None else 0

    # 按主键倒序展示最新用户，再应用当前页的偏移量和条数限制。
    user_statement = select(User).order_by(User.id.desc()).offset(offset).limit(limit)
    user_result = await db.scalars(user_statement)
    users = list(user_result.all())

    return users, total


# endregion


# region 管理员更新用户状态
async def update_user(
    db: AsyncSession,
    user_id: int,
    status: AdminUpdateRequest,
) -> User | None:
    """更新指定用户的启用状态，并返回更新后的用户对象。"""

    # get() 按主键查询；用户不存在时返回 None，由 Service 处理成 404。
    user = await db.get(User, user_id)
    if user is None:
        return None

    # 直接修改 ORM 对象，commit() 时 SQLAlchemy 会自动生成 UPDATE 语句。
    user.is_active = status.is_active
    await db.commit()
    await db.refresh(user)

    return user


# endregion


__all__ = ["get_user_list", "update_user"]
