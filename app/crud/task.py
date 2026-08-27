"""任务数据访问模块。

本模块只负责任务表的查询与写入，不处理 HTTP 响应或业务规则。
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


# region 任务查询
async def get_task_by_title(
    db: AsyncSession,
    user_id: int,
    title: str,
) -> Task | None:
    """根据所属用户和标题查询任务。"""

    # 必须同时限定 user_id，避免把其他用户的同名任务判断为冲突。
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.title == title,
    )

    return await db.scalar(statement)


# endregion


# region 任务创建
async def create_task(
    db: AsyncSession,
    user_id: int,
    title: str,
    description: str | None,
    status: str,
    priority: int,
    due_date: datetime | None,
) -> Task:
    """创建任务记录并返回数据库生成的完整对象。"""

    # user_id 来自已认证用户，客户端不能自行指定任务所属用户。
    new_task = Task(
        user_id=user_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
    )
    db.add(new_task)

    # 提交后刷新任务，取得主键、时间和数据库默认字段。
    await db.commit()
    await db.refresh(new_task)

    return new_task


# endregion


__all__ = ["create_task", "get_task_by_title"]
