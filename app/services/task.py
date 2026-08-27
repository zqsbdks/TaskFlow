"""任务业务服务。

Service 层负责执行任务业务规则，并在校验通过后调用 CRUD。
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task import create_task, get_task_by_id, get_task_by_title, get_task_list
from app.models.task import Task
from app.models.user import User
from app.schemas.task_request import TaskCreateRequest, TaskListRequest
from app.schemas.task_response import TaskCreateResponse, TaskListResponse


# region 任务创建服务
async def create_task_service(
    db: AsyncSession,
    current_user: User,
    task_data: TaskCreateRequest,
) -> Task:
    """检查当前用户的同名任务并创建新任务。"""

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


# region 任务列表服务
async def get_task_list_service(
    db: AsyncSession,
    current_user: User,
    query: TaskListRequest,
) -> TaskListResponse:
    """按分页及筛选条件获取当前用户的任务列表。"""

    # SQLAlchemy 的 offset 从 0 开始，因此需要根据当前页码换算偏移量。
    offset = (query.page - 1) * query.page_size
    tasks, total = await get_task_list(
        db=db,
        user_id=current_user.id,
        offset=offset,
        limit=query.page_size,
        task_status=query.status,
        priority=query.priority,
    )

    # 使用整数运算向上取整；没有任务时总页数为 0。
    total_pages = (total + query.page_size - 1) // query.page_size

    # 将 SQLAlchemy Task 对象显式转换为响应模型，确保字段安全并满足静态类型检查。
    task_items = [
        TaskCreateResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]

    return TaskListResponse(
        items=task_items,
        total=total,
        page=query.page,
        page_size=query.page_size,
        total_pages=total_pages,
    )


# endregion


# region 任务详情服务
async def get_task_detail_service(
    db: AsyncSession,
    current_user: User,
    task_id: int,
) -> Task:
    """查询当前用户拥有的指定任务。

    Args:
        db: 当前请求使用的异步数据库会话。
        current_user: 由访问令牌确定的当前登录用户。
        task_id: 路径参数中的任务主键。

    Returns:
        当前用户拥有的任务对象。

    Raises:
        HTTPException: 任务不存在或不属于当前用户时返回 HTTP 404。
    """

    # CRUD 已同时限定 task_id 和当前用户 ID，因此不会返回其他用户的任务。
    task = await get_task_by_id(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有找到任务",
        )

    return task


# endregion


__all__ = ["create_task_service", "get_task_detail_service", "get_task_list_service"]
