"""从 Authorization 请求头解析并验证 JWT Bearer 令牌。

基础模板只验证签名、算法、过期时间和 ``sub`` 声明，不绑定具体 User 表。
业务项目可以基于返回载荷继续加载用户、检查权限或执行令牌撤销校验。
"""

from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.dependencies.db import get_db
from app.models.user import User
from app.services.user import get_current_user_service

# auto_error=False 让缺少请求头的情况进入自定义逻辑，返回项目约定的中文提示。
bearer_scheme = HTTPBearer(auto_error=False)


# region 验证访问令牌
async def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    """校验 Bearer 令牌并返回 JWT 载荷。

    Args:
        credentials: FastAPI 从 Authorization 请求头解析出的 Bearer 凭据。

    Raises:
        HTTPException: 请求未携带令牌，或令牌无效、已过期时返回 401。

    Returns:
        dict[str, Any]: 已验证的 JWT 载荷，其中保证包含非空 ``sub``。
    """

    if not credentials:
        # 明确返回 Bearer 认证挑战头，客户端可以据此触发重新登录。
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 Authorization 请求头",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # PyJWT 会同时校验签名、允许的算法以及标准 exp 过期声明。
        # payload：签名、算法和有效期均校验通过后的 JWT 声明字典。
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        # 对外隐藏签名错误等内部细节，避免泄露安全实现信息。
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌或令牌已过期",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if not payload.get("sub"):
        # sub 是调用方身份的稳定标识，业务层通常用它查询用户或服务账号。
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="访问令牌缺少用户标识",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# endregion


# region 获取当前用户
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token_payload: dict[str, Any] = Depends(get_current_token_payload),
) -> User:
    """根据已验证 Token 中的 ``sub`` 查询当前用户。

    Args:
        db: FastAPI 为当前请求注入的异步数据库会话。
        token_payload: 已通过签名、算法和有效期校验的 JWT 载荷。

    Returns:
        Token 所属且当前处于启用状态的用户。

    Raises:
        HTTPException: ``sub`` 无效、用户不存在时返回 401；账号停用时返回 403。
    """

    # 登录签发 Token 时将用户主键转换成字符串写入 sub，这里再转换回整数。
    try:
        user_id = int(token_payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="访问令牌中的用户标识无效",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # 依赖层只解析认证信息，用户存在性和账号状态规则交由 Service 处理。
    return await get_current_user_service(
        db=db,
        user_id=user_id,
    )


# endregion


__all__ = ["get_current_token_payload", "get_current_user"]
