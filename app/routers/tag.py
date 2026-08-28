"""标签 API 路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.schemas.base import ResponseModel
from app.schemas.tag_request import TagCreateRequest
from app.schemas.tag_response import TagCreateResponse
from app.services.tag import create_tag_service

# 标签领域接口统一使用 /tags 路径前缀和中文 Swagger 标签。
tag_router = APIRouter(prefix="/tags", tags=["标签"])


# region 标签创建
@tag_router.post("/create", response_model=ResponseModel[TagCreateResponse])
async def create_tag(
    tag_data: TagCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """为当前登录用户创建标签并返回标签信息。"""

    # Router 只负责输入输出，重复检查和数据库创建交给 Service。
    new_tag = await create_tag_service(
        db=db,
        current_user=current_user,
        tag_data=tag_data,
    )

    # TagCreateResponse 会从 ORM 对象读取并筛选允许公开的字段。
    return ResponseModel(
        message="创建标签成功",
        data=new_tag,
    )


# endregion


__all__ = ["tag_router"]
