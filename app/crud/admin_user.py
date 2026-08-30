"""管理员用户数据访问模块。

本模块只负责用户表查询，不处理权限判断或 HTTP 响应。
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


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


__all__ = ["get_user_list"]
