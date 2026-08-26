"""用户业务服务。

Service 层位于 Router 与 CRUD 之间，负责组织注册规则、密码安全处理和数据库调用。
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.crud.user import create_user, get_user_by_username_or_email
from app.models.user import User
from app.schemas.user_request import UserRegisterRequest


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

    # 预先检查唯一字段，以便向客户端返回比数据库约束错误更明确的提示。
    existing_user = await get_user_by_username_or_email(
        db=db,
        username=user_data.username,
        email=user_data.email,
    )

    if existing_user is not None:
        # 根据命中的字段区分冲突原因，方便前端定位需要修改的输入项。
        if existing_user.username == user_data.username:
            detail = "用户名已存在"
        else:
            detail = "邮箱已被注册"

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    # 明文密码只在 Service 调用期间存在，进入 CRUD 前转换为不可逆哈希。
    password_hash = hash_password(user_data.password)

    return await create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
    )


__all__ = ["register_user_service"]
