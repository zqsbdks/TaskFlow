"""任务数据访问模块。

本模块只负责任务表的查询与写入，不处理 HTTP 响应或业务规则。
"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task
from app.models.task_tag import TaskTag


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


async def get_task_by_id(
    db: AsyncSession,
    user_id: int,
    task_id: int,
) -> Task | None:
    """根据任务 ID 查询当前用户拥有的任务。"""

    # 同时限制任务主键和所属用户，防止用户通过修改 task_id 查看他人的任务。
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.id == task_id,
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


# region 任务列表查询
async def get_task_list(
    db: AsyncSession,
    user_id: int,
    offset: int,
    limit: int,
    task_status: str | None,
    priority: int | None,
) -> tuple[list[Task], int]:
    """分页查询当前用户的任务，并返回符合条件的总条数。"""

    # 一条语句负责查询任务列表，另一条语句负责统计任务总数。
    task_statement = (
        select(Task)
        .options(selectinload(Task.task_tags).selectinload(TaskTag.tag))
        .where(Task.user_id == user_id)
    )
    count_statement = select(func.count(Task.id)).where(Task.user_id == user_id)

    # 如果传入了任务状态，两条查询都增加相同的状态条件。
    if task_status is not None:
        task_statement = task_statement.where(Task.status == task_status)
        count_statement = count_statement.where(Task.status == task_status)

    # 如果传入了优先级，两条查询都增加相同的优先级条件。
    if priority is not None:
        task_statement = task_statement.where(Task.priority == priority)
        count_statement = count_statement.where(Task.priority == priority)

    # 先执行数量查询；数据库没有返回数字时按 0 处理。
    count_result = await db.scalar(count_statement)
    if count_result is None:
        total = 0
    else:
        total = count_result

    # 给任务列表增加排序和分页条件，再执行查询。
    task_statement = (
        task_statement.order_by(Task.created_at.desc(), Task.id.desc()).offset(offset).limit(limit)
    )
    task_result = await db.scalars(task_statement)
    tasks = list(task_result.all())

    return tasks, total


# endregion


# region 任务更新
async def update_task(
    db: AsyncSession,
    task: Task,
    update_values: dict[str, object],
) -> Task:
    """更新指定字段并返回数据库中的最新任务对象。"""

    # update_values 只包含 Service 允许修改的字段，不会覆盖未提交的数据。
    for field_name, field_value in update_values.items():
        setattr(task, field_name, field_value)

    # 所有字段修改完成后只提交一次事务。
    await db.commit()
    await db.refresh(task)

    return task


# endregion


# region 任务删除
async def delete_task(db: AsyncSession, task: Task) -> None:
    """从数据库中删除指定任务。"""

    # Task 模型配置了级联删除，任务关联的 task_tag 记录会一并清理。
    await db.delete(task)
    await db.commit()


# endregion


# region 任务状态更新
async def update_task_status(
    db: AsyncSession,
    task: Task,
    status_value: str,
    completed_at: datetime | None,
) -> Task:
    """保存任务的新状态和对应的完成时间。"""

    # Service 已决定状态对应的完成时间，CRUD 只负责写入数据库。
    task.status = status_value
    task.completed_at = completed_at

    await db.commit()
    await db.refresh(task)

    return task


# endregion


__all__ = [
    "create_task",
    "delete_task",
    "get_task_by_id",
    "get_task_by_title",
    "get_task_list",
    "update_task",
    "update_task_status",
]
