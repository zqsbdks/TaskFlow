"""应用配置加载模块。

配置由 Pydantic Settings 统一解析。进程环境变量优先于项目根目录的 ``.env``，
因此同一份代码可以在本地、测试和生产环境使用不同配置而无需改动源码。
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """定义应用与 Alembic 共同使用的强类型运行配置。

    环境变量统一使用 ``APP_`` 前缀。例如字段 ``database_url`` 对应
    ``APP_DATABASE_URL``。未知字段被忽略，便于在共享环境文件中存放其他服务配置。
    """

    # 这里控制配置来源、编码和变量名前缀，不包含任何真实密码或密钥。
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )

    # project_name：OpenAPI 文档标题和日志中显示的项目名称。
    project_name: str = "FastAPI Starter"
    # debug：是否启用调试模式；生产环境必须关闭，避免响应泄露异常细节。
    debug: bool = False
    # api_v1_prefix：业务接口的统一版本前缀，便于未来同时维护多个 API 版本。
    api_v1_prefix: str = "/api/v1"

    # database_url：异步数据库连接地址；MySQL 必须使用 aiomysql 驱动。
    database_url: str = "mysql+aiomysql://username:password@localhost:3306/app?charset=utf8mb4"
    # database_echo：是否把 SQLAlchemy 执行的 SQL 输出到日志。
    database_echo: bool = False

    # log_level：应用允许输出的最低日志等级，例如 INFO 或 DEBUG。
    log_level: str = "INFO"
    # log_file：可选日志文件路径；留空时只输出到控制台。
    log_file: str | None = None

    # secret_key：JWT HMAC 签名密钥；生产环境应使用至少 32 字节的随机值。
    secret_key: str = "dev-only-change-me-before-production"
    # jwt_algorithm：JWT 的签名和验证算法，签发端与验证端必须保持一致。
    jwt_algorithm: str = "HS256"
    # access_token_expire_minutes：访问令牌有效时间，单位为分钟。
    access_token_expire_minutes: int = 30

    # redis_url：可选 Redis 连接地址；为空时不会创建客户端或初始化缓存。
    redis_url: str | None = None
    # redis_max_connections：Redis 连接池的最大连接数量，最小值为 1。
    redis_max_connections: int = Field(default=10, ge=1)
    # redis_timeout：单次 Redis 网络操作的超时时间，单位为秒且必须大于 0。
    redis_timeout: float = Field(default=5.0, gt=0)

    # cors_origins：允许跨域请求的来源列表；default_factory 避免实例间共享列表。
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])


@lru_cache
def get_settings() -> Settings:
    """创建并缓存当前进程唯一的配置对象。

    缓存可以避免每次依赖注入时重复读取和解析 ``.env``。测试若需要重新加载配置，
    可以调用 ``get_settings.cache_clear()`` 后再获取。
    """

    return Settings()


# 绝大多数模块直接复用该实例，保证数据库、JWT 和 Alembic 读取相同配置。
settings = get_settings()
