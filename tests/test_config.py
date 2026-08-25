"""验证 Settings 的数据库约束、默认值和可变字段隔离。"""

from app.core.config import Settings


def test_settings_accept_mysql_async_url() -> None:
    """显式传入的 aiomysql URL 应被保留，并继续带有默认 API 前缀。"""

    # _env_file=None 隔离开发机 .env，确保本测试只验证声明的输入和默认值。
    # settings：忽略本地 .env 后构造的独立配置实例，只包含显式输入和代码默认值。
    settings = Settings(
        _env_file=None,
        database_url="mysql+aiomysql://user:password@localhost/test",
    )

    assert settings.database_url.startswith("mysql+aiomysql://")
    assert settings.api_v1_prefix == "/api/v1"


def test_cors_origins_is_not_shared() -> None:
    """两个 Settings 实例不能共享同一个 CORS 列表对象。"""

    # first：用于执行列表修改的第一个独立配置实例。
    first = Settings(_env_file=None)
    # second：用于确认可变默认值没有被 first 共享的对照配置实例。
    second = Settings(_env_file=None)
    # 修改第一个实例后，第二个实例不应出现相同元素。
    first.cors_origins.append("https://example.com")

    assert "https://example.com" not in second.cors_origins
