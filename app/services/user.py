"""用户业务服务。

Service 层位于 Router 与 CRUD 之间，负责组织注册规则、密码安全处理和数据库调用。
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.core.token import create_access_token
from app.crud.user import create_user, get_user_by_email, get_user_by_username
from app.models.user import User
from app.schemas.user_request import UserLoginRequest, UserRegisterRequest
from app.schemas.user_response import UserLoginInfo, UserLoginResponse


# region 用户注册服务
async def register_user_service(
    db: AsyncSession,
    user_data: UserRegisterRequest,
) -> User:
    """校验注册信息、哈希密码并创建用户。

    Args:
        db: 当前请求使用的异步数据库会话。
        user_data: 已通过 Pydantic 基础格式校验的注册请求数据。

    Returns:
        注册成功后创建的用户对象。

    Raises:
        HTTPException: 用户名或邮箱已被占用时返回 HTTP 409。
    """

    # 分别检查两个唯一字段，以便向客户端返回准确的冲突原因。
    existing_user = await get_user_by_username(
        db=db,
        username=user_data.username,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在",
        )

    existing_user = await get_user_by_email(
        db=db,
        email=user_data.email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="邮箱已被注册",
        )

    # 明文密码只在 Service 调用期间存在，进入 CRUD 前转换为不可逆哈希。
    password_hash = hash_password(user_data.password)

    return await create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
    )


# endregion


# region 用户登录服务
async def login_user_service(
    db: AsyncSession,
    user_data: UserLoginRequest,
) -> UserLoginResponse:
    """验证邮箱和密码，并为可用账号签发访问令牌。

    Args:
        db: 当前请求使用的异步数据库会话。
        user_data: 已通过格式校验的登录邮箱和明文密码。

    Returns:
        包含 JWT 和用户公开信息的登录响应数据。

    Raises:
        HTTPException: 邮箱或密码错误时返回 401，账号停用时返回 403。
    """

    # email 具有唯一约束，因此这里返回的就是本次登录邮箱对应的唯一用户记录。
    existing_user = await get_user_by_email(
        db=db,
        email=user_data.email,
    )

    # 邮箱不存在和密码错误使用相同提示，避免泄露已注册账号信息。
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 必须使用上面按邮箱查到的同一条用户记录中的 password_hash 进行验证，
    # 不会读取或匹配其他邮箱对应用户的密码哈希。
    password_is_valid = verify_password(user_data.password, existing_user.password_hash)
    if not password_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 密码正确后仍需检查账号状态，停用账号不能获得新的访问令牌。
    if not existing_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被停用",
        )

    # sub 使用字符串形式的用户主键，后续认证依赖可据此识别当前用户。
    token = create_access_token({"sub": str(existing_user.id)})

    # 显式挑选允许返回的字段，确保 password_hash 等敏感属性不会进入响应。
    return UserLoginResponse(
        token=token,
        userinfo=UserLoginInfo(
            id=existing_user.id,
            username=existing_user.username,
            email=existing_user.email,
            role=existing_user.role,
        ),
    )


# endregion


__all__ = ["login_user_service", "register_user_service"]
