"""用户数据表的 SQLAlchemy ORM 模型。"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.task import Task


class User(Base):
    """保存用户登录信息、角色、账号状态及其任务关系。"""

    # __tablename__：模型对应的数据库表名。
    __tablename__ = "user"
    # __table_args__：设置表级中文说明以及支持中文和表情符号的字符集。
    __table_args__ = {
        "comment": "用户信息表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    # id：自增用户主键，用于唯一标识一名用户。
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="用户主键",
    )
    # username：用户登录名；唯一索引可防止创建重名账号并加速登录查询。
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        comment="用户登录名",
    )
    # email：用户邮箱地址，用于登录、通知或找回密码，数据库中不可重复。
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        comment="用户邮箱地址",
    )
    # password_hash：使用 Argon2 生成的不可逆密码哈希，禁止保存明文密码。
    password_hash: Mapped[str] = mapped_column(String(255), comment="Argon2 密码哈希")
    # role：用户角色标识，默认普通用户；后续可用于区分 user 和 admin。
    role: Mapped[str] = mapped_column(
        String(30),
        server_default=text("'user'"),
        comment="用户角色",
    )
    # is_active：账号是否允许登录；禁用账号时保留其任务和历史数据。
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("1"),
        comment="账号是否启用",
    )
    # created_at：用户记录首次写入数据库的时间。
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="创建时间",
    )
    # updated_at：用户资料最近一次更新的时间。
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    # tasks：当前用户拥有的全部任务；删除用户时数据库会级联删除这些任务。
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    ) 
