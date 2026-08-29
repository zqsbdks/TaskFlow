"""任务与标签关联表的数据访问模块。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task_tag import TaskTag


# region 任务标签关联查询
async def get_task_tag(
    db: AsyncSession,
    task_id: int,
    tag_id: int,
) -> TaskTag | None:
    """根据任务 ID 和标签 ID 查询已有的绑定关系。"""

    statement = select(TaskTag).where(
        TaskTag.task_id == task_id,
        TaskTag.tag_id == tag_id,
    )

    return await db.scalar(statement)


# endregion


# region 任务标签关联创建
async def add_tag_to_task(
    db: AsyncSession,
    task_id: int,
    tag_id: int,
) -> TaskTag:
    """创建任务与标签的绑定关系。"""

    # task_id 和 tag_id 已由 Service 完成归属及重复校验。
    task_tag = TaskTag(
        task_id=task_id,
        tag_id=tag_id,
    )
    db.add(task_tag)

    # 提交后刷新，取得数据库自动生成的关联创建时间。
    await db.commit()
    await db.refresh(task_tag)

    return task_tag


# endregion


# region 任务标签关联删除
async def delete_task_tag(
    db: AsyncSession,
    task_tag: TaskTag,
) -> None:
    """删除指定的任务标签绑定记录。"""

    # Service 已确认关联记录存在，CRUD 只负责删除并提交事务。
    await db.delete(task_tag)
    await db.commit()


# endregion


__all__ = ["add_tag_to_task", "delete_task_tag", "get_task_tag"]
