"""用户 API 路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.schemas.base import ResponseModel
from app.schemas.user_request import UserLoginRequest, UserRegisterRequest, UserUpdateRequest
from app.schemas.user_response import (
    UserInfo,
    UserLoginResponse,
    UserRegisterResponse,
    UserUpdataResponse,
)
from app.services.user import login_user_service, register_user_service, update_user_service

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

    # 直接传入 ORM 用户对象，路由声明的 UserRegisterResponse 会筛选可公开字段。
    return ResponseModel(
        message="注册成功",
        data=new_user,
    )


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

    # Service 已组装好 Token 和用户信息，此处只添加统一响应外层。
    return ResponseModel(
        message="登录成功",
        data=login_result,
    )


# endregion


# region 当前用户信息
@user_router.get("/info", response_model=ResponseModel[UserInfo])
async def get_user_info(
    current_user: User = Depends(get_current_user),
):
    """返回当前有效 Token 对应的用户公开信息。"""

    # UserInfo 响应模型会从当前用户对象读取并保留允许返回的字段。
    return ResponseModel(
        message="获取用户信息成功",
        data=current_user,
    )


# endregion


# region 用户信息更新
@user_router.put(
    "/update",
    response_model=ResponseModel[UserUpdataResponse],
)
async def update_user_info(
    user_data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """接收当前用户的信息修改请求，并返回更新后的公开信息。"""

    # Router 负责接收请求；重复检查和数据库更新统一交给 Service。
    user = await update_user_service(
        db=db,
        current_user=current_user,
        user_data=user_data,
    )

    # 直接返回更新后的 ORM 对象，由 UserUpdataResponse 控制 data 的字段结构。
    return ResponseModel(
        message="更新成功",
        data=user,
    )


# endregion
