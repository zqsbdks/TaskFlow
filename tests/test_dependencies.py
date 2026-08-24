"""验证 JWT Bearer 认证依赖的成功与缺少凭据分支。"""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.token import create_access_token
from app.dependencies.auth import get_current_token_payload


@pytest.mark.asyncio
async def test_current_token_payload_returns_token_payload() -> None:
    """有效令牌应通过签名校验并原样返回 sub 声明。"""

    # 使用正式签发函数生成令牌，覆盖签发与认证依赖之间的兼容性。
    token = create_access_token({"sub": "test-user"})
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    payload = await get_current_token_payload(credentials)

    assert payload["sub"] == "test-user"


@pytest.mark.asyncio
async def test_current_token_payload_rejects_missing_credentials() -> None:
    """缺少 Authorization 请求头时应返回 401。"""

    # 直接调用依赖函数，精确验证异常类型和状态码。
    with pytest.raises(HTTPException) as exc_info:
        await get_current_token_payload(None)

    assert exc_info.value.status_code == 401
