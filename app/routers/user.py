"""用户 API 路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.schemas.base import ResponseModel
from app.schemas.user_request import UserRegisterRequest
from app.schemas.user_response import UserRegisterResponse
from app.services.user import register_user_service

# 用户领域的所有接口共享 /users 路径前缀和 Swagger 分组标签。
user_router = APIRouter(tags=["用户"], prefix="/users")


@user_router.post("/register", response_model=ResponseModel[UserRegisterResponse])
async def register_user(
    user_data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """接收用户注册请求并返回统一格式的用户信息。

    Args:
        user_data: 用户名、邮箱和明文密码组成的注册请求体。
        db: FastAPI 为当前请求注入的异步数据库会话。

    Returns:
        包含新用户公开字段的统一成功响应；密码哈希不会进入响应。
    """

    # Router 只负责 HTTP 输入输出，注册规则和密码处理统一交给 Service。
    new_user = await register_user_service(
        db=db,
        user_data=user_data,
    )

    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
        },
    }
