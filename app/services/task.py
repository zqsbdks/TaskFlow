"""任务业务服务。

Service 层负责执行任务业务规则，并在校验通过后调用 CRUD。
"""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task import (
    create_task,
    delete_task,
    get_task_by_id,
    get_task_by_title,
    get_task_list,
    update_task,
    update_task_status,
)
from app.models.task import Task
from app.models.user import User
from app.schemas.task_request import (
    TaskCreateRequest,
    TaskListRequest,
    TaskStatusUpdateRequest,
    TaskUpdateRequest,
)


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
) -> dict[str, object]:
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

    # 直接返回 ORM 列表和分页数据，由 Router 的 response_model 完成字段过滤与序列化。
    return {
        "items": tasks,
        "total": total,
        "page": query.page,
        "page_size": query.page_size,
        "total_pages": total_pages,
    }


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


# region 任务更新服务
async def update_task_service(
    db: AsyncSession,
    current_user: User,
    task_id: int,
    update_data: TaskUpdateRequest,
) -> Task:
    """校验任务归属及更新内容，然后更新当前用户的任务。"""

    # 同时按任务 ID 和当前用户 ID 查询，禁止修改其他用户的任务。
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

    # exclude_unset=True 确保请求中没有提交的字段不会被错误更新为 None。
    update_values = update_data.model_dump(exclude_unset=True)
    if not update_values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有提供需要更新的字段",
        )

    # title 和 priority 对应数据库非空字段，不能显式更新为 null。
    for field_name in ("title", "priority"):
        if field_name in update_values and update_values[field_name] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} 不能为 null",
            )

    # 修改标题时检查当前用户是否已有另一个同名任务。
    new_title = update_values.get("title")
    if isinstance(new_title, str) and new_title != task.title:
        existing_task = await get_task_by_title(
            db=db,
            user_id=current_user.id,
            title=new_title,
        )
        if existing_task is not None and existing_task.id != task.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="任务标题已存在",
            )

    return await update_task(
        db=db,
        task=task,
        update_values=update_values,
    )


# endregion


# region 任务删除服务
async def delete_task_service(
    db: AsyncSession,
    current_user: User,
    task_id: int,
) -> None:
    """查询并删除当前用户拥有的指定任务。

    Args:
        db: 当前请求使用的异步数据库会话。
        current_user: 由访问令牌确定的当前登录用户。
        task_id: 路径参数中的任务主键。

    Raises:
        HTTPException: 任务不存在或不属于当前用户时返回 HTTP 404。
    """

    # 同时按 task_id 和当前用户 ID 查询，防止删除其他用户的任务。
    task = await get_task_by_id(
        db=db,
        user_id=current_user.id,
        task_id=task_id,
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    # 权限校验通过后，交由 CRUD 执行数据库删除。
    await delete_task(db=db, task=task)


# endregion


# region 任务状态更新服务
async def update_task_status_service(
    db: AsyncSession,
    current_user: User,
    task_id: int,
    status_data: TaskStatusUpdateRequest,
) -> Task:
    """校验任务归属并更新任务状态及完成时间。

    Args:
        db: 当前请求使用的异步数据库会话。
        current_user: 由访问令牌确定的当前登录用户。
        task_id: 路径参数中的任务主键。
        status_data: 请求体中必传的新任务状态。

    Returns:
        状态更新成功后的任务对象。

    Raises:
        HTTPException: 任务不存在或状态没有发生变化时返回错误。
    """

    # 同时按 task_id 和当前用户 ID 查询，禁止修改其他用户的任务状态。
    task = await get_task_by_id(
        db=db,
        user_id=current_user.id,
        task_id=task_id,
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在",
        )

    # 检查原状态和新状态是否一样，如果一样则不更新
    if task.status == status_data.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务状态未改变",
        )

    # 已完成状态记录当前时间；其他状态清空旧的完成时间。
    if status_data.status == "completed":
        completed_at = datetime.now()
    else:
        completed_at = None

    return await update_task_status(
        db=db,
        task=task,
        status_value=status_data.status,
        completed_at=completed_at,
    )


# endregion


__all__ = [
    "create_task_service",
    "delete_task_service",
    "get_task_detail_service",
    "get_task_list_service",
    "update_task_service",
    "update_task_status_service",
]
