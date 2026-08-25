"""验证 Argon2 密码处理和 JWT 签发/解析的核心安全行为。"""

import jwt

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.core.token import create_access_token


def test_password_hash_and_verify() -> None:
    """正确密码应通过，错误密码应被拒绝。"""

    # password_hash：由 Argon2 生成的不可逆密码哈希，不应等于原始明文密码。
    password_hash = hash_password("correct-password")

    # 同时覆盖正向和反向分支，防止验证函数意外恒为 True。
    assert verify_password("correct-password", password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_access_token_round_trip() -> None:
    """签发后的 JWT 应能用同一密钥解码，并包含 sub 与 exp。"""

    # token：包含测试用户标识和默认过期时间的已签名 JWT 字符串。
    token = create_access_token({"sub": "test-user"})
    # 显式限制算法可以防止解码端接受攻击者指定的其他算法。
    # payload：使用相同密钥和限定算法解码后得到的 JWT 声明字典。
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == "test-user"
    assert "exp" in payload
