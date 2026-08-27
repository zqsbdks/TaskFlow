"""任务业务服务。

Service 层负责执行任务业务规则，并在校验通过后调用 CRUD。
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task import create_task, get_task_by_title
from app.models.task import Task
from app.models.user import User
from app.schemas.task_request import TaskCreateRequest


# region 任务创建服务
async def create_task_service(
    db: AsyncSession,
    current_user: User,
    task_data: TaskCreateRequest,
) -> Task:
    """检查当前用户的同名任务并创建新任务。

    Args:
        db: 当前请求使用的异步数据库会话。
        current_user: 由访问令牌确定的当前登录用户。
        task_data: 已通过 Pydantic 格式校验的任务数据。

    Returns:
        创建成功后的任务对象。

    Raises:
        HTTPException: 当前用户已存在同名任务时返回 HTTP 409。
    """

    # 只检查当前用户自己的任务，其他用户可以使用相同标题。
    existing_task = await get_task_by_title(
        db=db,
        user_id=current_user.id,
        title=task_data.title,
    )
    if existing_task is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="任务标题已存在",
        )

    # 业务校验通过后，将经过验证的字段交给 CRUD 保存。
    return await create_task(
        db=db,
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
    )


# endregion


__all__ = ["create_task_service"]
