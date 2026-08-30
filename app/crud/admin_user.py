"""管理员用户数据访问模块。

本模块只负责用户表查询，不处理权限判断或 HTTP 响应。
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.user import User


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


# region 管理员任务列表查询
async def get_all_task_list(
    db: AsyncSession,
    offset: int,
    limit: int,
) -> tuple[list[Task], int]:
    """分页查询所有用户的任务，并返回任务总数。"""

    # 数量查询不限制 user_id，也不应用分页，用于计算全部任务的页数。
    count_statement = select(func.count(Task.id))
    count_result = await db.scalar(count_statement)
    total = count_result if count_result is not None else 0

    # 按主键倒序返回最新任务，再应用当前页偏移量和每页条数。
    task_statement = select(Task).order_by(Task.id.desc()).offset(offset).limit(limit)
    task_result = await db.scalars(task_statement)
    tasks = list(task_result.all())

    return tasks, total


# endregion


# region 管理员用户查询


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """按主键查询用户，并返回用户对象。"""

    return await db.get(User, user_id)


# endregion


# region 管理员更新用户状态


async def update_user(
    db: AsyncSession,
    user: User,
    is_active: bool,
) -> User:
    """更新指定用户的启用状态，并返回更新后的用户对象。"""

    # 直接修改 ORM 对象，commit() 时 SQLAlchemy 会自动生成 UPDATE 语句。
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)

    return user


# endregion


# region 管理员删除用户


async def delete_user(db: AsyncSession, user: User) -> None:
    """删除指定用户并提交事务。"""

    # User 模型及其外键配置会级联清理该用户的任务、标签和关联记录。
    await db.delete(user)
    await db.commit()


# endregion


__all__ = [
    "delete_user",
    "get_all_task_list",
    "get_user_by_id",
    "get_user_list",
    "update_user",
]
