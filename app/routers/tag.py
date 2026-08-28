"""标签 API 路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.schemas.base import ResponseModel
from app.schemas.tag_request import TagCreateRequest
from app.schemas.tag_response import TagCreateResponse, TagListResponse
from app.services.tag import create_tag_service, get_tag_list_service

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


# region 标签列表
@tag_router.get("/list", response_model=ResponseModel[list[TagListResponse]])
async def get_tag_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前登录用户创建的全部标签。"""

    # Router 只负责输入输出，用户范围限制和列表查询交给 Service。
    tags = await get_tag_list_service(db=db, current_user=current_user)

    # data 是由多个标签对象组成的列表，响应模型负责筛选公开字段。
    return ResponseModel(
        message="获取标签列表成功",
        data=tags,
    )


# endregion


__all__ = ["tag_router"]
