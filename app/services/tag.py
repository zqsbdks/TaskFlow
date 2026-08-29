"""标签业务服务。"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.tag import create_tag, get_tag_by_id, get_tag_by_name, get_tags_by_user_id
from app.crud.task import get_task_by_id
from app.crud.task_tag import add_tag_to_task, delete_task_tag, get_task_tag
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag_request import TagCreateRequest


# region 标签创建服务
async def create_tag_service(
    db: AsyncSession,
    current_user: User,
    tag_data: TagCreateRequest,
) -> Tag:
    """检查当前用户的同名标签并创建新标签。

    Args:
        db: 当前请求使用的异步数据库会话。
        current_user: 由访问令牌确定的当前登录用户。
        tag_data: 已通过 Pydantic 格式校验的标签数据。

    Returns:
        创建成功后的标签对象。

    Raises:
        HTTPException: 当前用户已存在同名标签时返回 HTTP 409。
    """

    # 只检查当前用户自己的标签，其他用户可以使用相同名称。
    existing_tag = await get_tag_by_name(
        db=db,
        user_id=current_user.id,
        name=tag_data.name,
    )
    if existing_tag is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="标签名称已存在",
        )

    # 业务校验通过后，交由 CRUD 写入当前用户的标签。
    return await create_tag(
        db=db,
        user_id=current_user.id,
        name=tag_data.name,
        color=tag_data.color,
    )


# endregion


# region 标签列表服务
async def get_tag_list_service(
    db: AsyncSession,
    current_user: User,
) -> list[Tag]:
    """获取当前用户的标签列表。

    Args:
        db: 当前请求使用的异步数据库会话。
        current_user: 由访问令牌确定的当前登录用户。

    Returns:
        当前用户的标签列表。
    """

    # 当前用户 ID 由令牌确定，只查询该用户自己创建的标签。
    return await get_tags_by_user_id(db=db, user_id=current_user.id)


# endregion


# region 为任务添加标签服务
async def add_tag_for_task_service(
    db: AsyncSession,
    current_user: User,
    task_id: int,
    tag_id: int,
) -> Tag:
    """校验任务和标签归属，然后建立绑定关系。

    Args:
        db: 当前请求使用的异步数据库会话。
        current_user: 由访问令牌确定的当前登录用户。
        task_id: 需要添加标签的任务 ID。
        tag_id: 需要绑定到任务的标签 ID。

    Returns:
        成功绑定到任务的标签对象。

    Raises:
        HTTPException: 任务或标签不存在时返回 404，已经绑定时返回 409。
    """

    # 查询条件包含当前用户 ID，确保不能操作其他用户的任务。
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

    # 标签也必须属于当前用户，不能把其他用户的标签绑定到自己的任务。
    tag = await get_tag_by_id(
        db=db,
        user_id=current_user.id,
        tag_id=tag_id,
    )
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在",
        )

    # 联合主键虽然能阻止重复数据，但提前检查可以返回清晰的 409 错误。
    existing_task_tag = await get_task_tag(
        db=db,
        task_id=task_id,
        tag_id=tag_id,
    )
    if existing_task_tag is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="任务已经添加了该标签",
        )

    # 所有业务校验通过后，交给关联表 CRUD 完成数据库写入。
    await add_tag_to_task(
        db=db,
        task_id=task_id,
        tag_id=tag_id,
    )

    return tag


# endregion


# region 从任务移除标签服务
async def remove_tag_from_task_service(
    db: AsyncSession,
    current_user: User,
    task_id: int,
    tag_id: int,
) -> None:
    """校验任务、标签和绑定关系，然后移除任务标签。

    Args:
        db: 当前请求使用的异步数据库会话。
        current_user: 由访问令牌确定的当前登录用户。
        task_id: 需要移除标签的任务 ID。
        tag_id: 需要从任务移除的标签 ID。

    Raises:
        HTTPException: 任务、标签或二者的绑定关系不存在时返回 HTTP 404。
    """

    # 查询条件包含当前用户 ID，确保不能修改其他用户的任务。
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

    # 标签也必须属于当前用户，不能操作其他用户创建的标签。
    tag = await get_tag_by_id(
        db=db,
        user_id=current_user.id,
        tag_id=tag_id,
    )
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在",
        )

    # 查询任务与标签的绑定记录；未绑定时不能返回删除成功。
    task_tag = await get_task_tag(
        db=db,
        task_id=task_id,
        tag_id=tag_id,
    )
    if task_tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务未添加该标签",
        )

    # 业务校验通过后，交给关联表 CRUD 删除绑定记录。
    await delete_task_tag(db=db, task_tag=task_tag)


# endregion


__all__ = [
    "add_tag_for_task_service",
    "create_tag_service",
    "get_tag_list_service",
    "remove_tag_from_task_service",
]
