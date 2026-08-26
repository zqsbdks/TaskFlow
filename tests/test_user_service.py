"""用户登录 Service 的单元测试。"""

from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.models.user import User
from app.schemas.user_request import UserLoginRequest
from app.services import user as user_service


def build_user(*, is_active: bool = True) -> User:
    """构造无需连接数据库的测试用户对象。"""

    return User(
        id=1,
        username="test-user",
        email="user@example.com",
        password_hash="stored-password-hash",
        role="user",
        is_active=is_active,
    )


@pytest.mark.asyncio
async def test_login_user_service_returns_token_and_user_info(monkeypatch) -> None:
    """凭据正确且账号可用时应返回 Token 和公开用户信息。"""

    user = build_user()
    monkeypatch.setattr(user_service, "get_user_by_email", AsyncMock(return_value=user))
    monkeypatch.setattr(user_service, "verify_password", lambda *_: True)
    monkeypatch.setattr(user_service, "create_access_token", lambda data: f"token-{data['sub']}")

    result = await user_service.login_user_service(
        db=AsyncMock(),
        user_data=UserLoginRequest(email=user.email, password="correct-password"),
    )

    assert result.token == "token-1"
    assert result.userinfo.id == user.id
    assert result.userinfo.email == user.email


@pytest.mark.asyncio
@pytest.mark.parametrize("user,password_is_valid", [(None, False), (build_user(), False)])
async def test_login_user_service_rejects_invalid_credentials(
    monkeypatch,
    user: User | None,
    password_is_valid: bool,
) -> None:
    """邮箱不存在或密码错误时均应返回相同的 401 提示。"""

    monkeypatch.setattr(user_service, "get_user_by_email", AsyncMock(return_value=user))
    monkeypatch.setattr(user_service, "verify_password", lambda *_: password_is_valid)

    with pytest.raises(HTTPException) as exc_info:
        await user_service.login_user_service(
            db=AsyncMock(),
            user_data=UserLoginRequest(email="user@example.com", password="wrong-password"),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "邮箱或密码错误"


@pytest.mark.asyncio
async def test_login_user_service_rejects_inactive_user(monkeypatch) -> None:
    """密码正确但账号停用时不应签发 Token。"""

    monkeypatch.setattr(
        user_service,
        "get_user_by_email",
        AsyncMock(return_value=build_user(is_active=False)),
    )
    monkeypatch.setattr(user_service, "verify_password", lambda *_: True)

    with pytest.raises(HTTPException) as exc_info:
        await user_service.login_user_service(
            db=AsyncMock(),
            user_data=UserLoginRequest(email="user@example.com", password="correct-password"),
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "账号已被停用"


# region 当前用户 Service 测试
@pytest.mark.asyncio
async def test_current_user_service_returns_active_user(monkeypatch) -> None:
    """用户存在且启用时应返回对应用户对象。"""

    user = build_user()
    get_user_by_id = AsyncMock(return_value=user)
    monkeypatch.setattr(user_service, "get_user_by_id", get_user_by_id)

    result = await user_service.get_current_user_service(
        db=AsyncMock(),
        user_id=user.id,
    )

    assert result is user


@pytest.mark.asyncio
async def test_current_user_service_rejects_missing_user(monkeypatch) -> None:
    """Token 对应用户不存在时应返回 401。"""

    monkeypatch.setattr(user_service, "get_user_by_id", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc_info:
        await user_service.get_current_user_service(
            db=AsyncMock(),
            user_id=1,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "访问令牌对应的用户不存在"


@pytest.mark.asyncio
async def test_current_user_service_rejects_inactive_user(monkeypatch) -> None:
    """Token 对应账号停用时应返回 403。"""

    monkeypatch.setattr(
        user_service,
        "get_user_by_id",
        AsyncMock(return_value=build_user(is_active=False)),
    )

    with pytest.raises(HTTPException) as exc_info:
        await user_service.get_current_user_service(
            db=AsyncMock(),
            user_id=1,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "账号已被停用"


# endregion
