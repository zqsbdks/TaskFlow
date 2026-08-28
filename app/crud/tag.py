"""标签数据访问模块。

本模块只负责标签表的查询与写入，不处理 HTTP 响应或业务规则。
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag


# region 标签查询
async def get_tag_by_name(
    db: AsyncSession,
    user_id: int,
    name: str,
) -> Tag | None:
    """根据所属用户和标签名称查询标签。"""

    # 同一用户不能创建重名标签，但不同用户可以使用相同名称。
    statement = select(Tag).where(
        Tag.user_id == user_id,
        Tag.name == name,
    )

    return await db.scalar(statement)


# endregion


# region 标签创建
async def create_tag(
    db: AsyncSession,
    user_id: int,
    name: str,
    color: str | None,
) -> Tag:
    """创建标签记录并返回数据库生成的完整对象。"""

    # user_id 来自当前认证用户，客户端不能自行指定标签所有者。
    new_tag = Tag(
        user_id=user_id,
        name=name,
        color=color,
    )
    db.add(new_tag)

    # 提交并刷新，以取得数据库生成的主键和创建时间。
    await db.commit()
    await db.refresh(new_tag)

    return new_tag


# endregion


__all__ = ["create_tag", "get_tag_by_name"]
