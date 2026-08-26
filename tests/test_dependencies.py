"""验证 JWT Bearer 认证依赖的成功与缺少凭据分支。"""

from unittest.mock import ANY, AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.token import create_access_token
from app.dependencies import auth as auth_dependencies
from app.dependencies.auth import get_current_token_payload
from app.models.user import User


@pytest.mark.asyncio
async def test_current_token_payload_returns_token_payload() -> None:
    """有效令牌应通过签名校验并原样返回 sub 声明。"""

    # token：使用测试用户标识签发的有效 JWT 字符串。
    # 使用正式签发函数生成令牌，覆盖签发与认证依赖之间的兼容性。
    token = create_access_token({"sub": "test-user"})
    # credentials：模拟 FastAPI 从 Authorization 请求头解析出的 Bearer 凭据。
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    # payload：通过签名、算法、过期时间及 sub 校验后的 JWT 载荷。
    payload = await get_current_token_payload(credentials)

    assert payload["sub"] == "test-user"


@pytest.mark.asyncio
async def test_current_token_payload_rejects_missing_credentials() -> None:
    """缺少 Authorization 请求头时应返回 401。"""

    # exc_info：pytest 捕获到的 HTTPException 信息，供后续检查状态码。
    # 直接调用依赖函数，精确验证异常类型和状态码。
    with pytest.raises(HTTPException) as exc_info:
        await get_current_token_payload(None)

    assert exc_info.value.status_code == 401


# region 获取当前用户依赖测试
def build_user(*, is_active: bool = True) -> User:
    """构造无需连接数据库的认证测试用户。"""

    return User(
        id=1,
        username="test-user",
        email="user@example.com",
        password_hash="stored-password-hash",
        role="user",
        is_active=is_active,
    )


@pytest.mark.asyncio
async def test_current_user_returns_user_from_token_subject(monkeypatch) -> None:
    """有效的用户 ID 应转换后交给当前用户 Service。"""

    user = build_user()
    get_current_user_service = AsyncMock(return_value=user)
    monkeypatch.setattr(
        auth_dependencies,
        "get_current_user_service",
        get_current_user_service,
    )

    result = await auth_dependencies.get_current_user(
        db=AsyncMock(),
        token_payload={"sub": "1"},
    )

    assert result is user
    get_current_user_service.assert_awaited_once_with(db=ANY, user_id=1)


@pytest.mark.asyncio
async def test_current_user_rejects_invalid_subject() -> None:
    """无法转换成用户主键的 sub 应返回 401。"""

    with pytest.raises(HTTPException) as exc_info:
        await auth_dependencies.get_current_user(
            db=AsyncMock(),
            token_payload={"sub": "not-an-integer"},
        )

    assert exc_info.value.status_code == 401


# endregion
