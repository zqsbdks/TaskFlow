"""用户 API 路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.schemas.base import ResponseModel
from app.schemas.user_request import UserLoginRequest, UserRegisterRequest
from app.schemas.user_response import UserLoginResponse, UserRegisterResponse
from app.services.user import login_user_service, register_user_service

# 用户领域的所有接口共享 /users 路径前缀和 Swagger 分组标签。
user_router = APIRouter(tags=["用户"], prefix="/users")


# region 用户注册
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


# endregion


# region 用户登录
@user_router.post("/login", response_model=ResponseModel[UserLoginResponse])
async def login_user(
    user_data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """接收登录请求并返回访问令牌及用户公开信息。

    Args:
        user_data: 登录邮箱和明文密码组成的请求体。
        db: FastAPI 为当前请求注入的异步数据库会话。

    Returns:
        包含 JWT 和公开用户字段的统一成功响应。
    """

    # 邮箱查询、密码验证、账号状态检查和 Token 签发均由 Service 完成。
    login_result = await login_user_service(
        db=db,
        user_data=user_data,
    )

    return ResponseModel(
        code=200,
        message="登录成功",
        data=login_result,
    )


# endregion
