"""标签业务服务。"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.tag import create_tag, get_tag_by_name, get_tags_by_user_id
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


__all__ = ["create_tag_service", "get_tag_list_service"]
