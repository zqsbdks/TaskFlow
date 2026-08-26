"""用户数据访问模块。

本模块只负责用户表的查询与写入，不处理 HTTP 响应、注册规则或明文密码哈希。
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


# region 用户查询
async def get_user_by_id(
    db: AsyncSession,
    user_id: int,
) -> User | None:
    """根据主键查询用户。

    Args:
        db: 当前请求使用的异步数据库会话。
        user_id: JWT 的 ``sub`` 声明所指向的用户主键。

    Returns:
        查询到的用户；主键不存在时返回 ``None``。
    """

    statement = select(User).where(User.id == user_id)

    return await db.scalar(statement)


async def get_user_by_username(
    db: AsyncSession,
    username: str,
) -> User | None:
    """根据用户名查询已存在的用户。

    Args:
        db: 当前请求使用的异步数据库会话。
        username: 待检查的用户名。

    Returns:
        查询到的用户；用户名未被占用时返回 ``None``。
    """

    statement = select(User).where(User.username == username)

    return await db.scalar(statement)


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    """根据邮箱查询已存在的用户。

    Args:
        db: 当前请求使用的异步数据库会话。
        email: 待检查的邮箱地址。

    Returns:
        查询到的用户；邮箱未被占用时返回 ``None``。
    """

    # 登录只需要先按唯一邮箱定位用户；密码必须用安全模块和该用户的哈希单独验证。
    statement = select(User).where(User.email == email)

    return await db.scalar(statement)


# endregion


# region 用户创建
async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password_hash: str,
) -> User:
    """创建用户记录并返回数据库生成的完整对象。

    Args:
        db: 当前请求使用的异步数据库会话。
        username: 新用户的登录名。
        email: 新用户的邮箱地址。
        password_hash: Service 层生成的密码哈希，不能传入明文密码。

    Returns:
        已提交并刷新过的用户对象。
    """

    # role、is_active 和时间字段由数据库模型中的默认值自动填充。
    new_user = User(username=username, email=email, password_hash=password_hash)
    db.add(new_user)

    # CRUD 明确提交本次写入；若提交失败，请求级数据库依赖会负责回滚事务。
    await db.commit()
    # 重新读取自增主键及数据库默认字段，确保响应阶段可以直接序列化。
    await db.refresh(new_user)

    return new_user


# endregion
