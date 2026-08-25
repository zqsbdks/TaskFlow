"""标签数据表的 SQLAlchemy ORM 模型。"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.task_tag import TaskTag
    from app.models.user import User


class Tag(Base):
    """保存可复用于多个任务的标签名称和显示颜色。"""

    # __tablename__：模型对应的数据库表名。
    __tablename__ = "tag"
    # __table_args__：同一用户不能创建重名标签，不同用户可以使用相同标签名称。
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="user_name"),
        {
            "comment": "标签信息表",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    # id：自增标签主键，用于在任务标签关联表中引用该标签。
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="标签主键",
    )
    # user_id：标签所属用户的主键；用户删除时由数据库级联删除其标签。
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
        comment="所属用户主键",
    )
    # name：标签显示名称；唯一约束只限制同一用户不能创建重名标签。
    name: Mapped[str] = mapped_column(
        String(50),
        comment="标签名称",
    )
    # color：可选的十六进制显示颜色，例如 #3B82F6，具体格式由应用层校验。
    color: Mapped[str | None] = mapped_column(
        String(7),
        nullable=True,
        comment="标签显示颜色",
    )
    # created_at：标签记录首次写入数据库的时间。
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("(now())"),
        comment="创建时间",
    )

    # user：创建并拥有当前标签的用户对象。
    user: Mapped["User"] = relationship(back_populates="tags")
    # task_tags：所有引用当前标签的任务关联记录。
    task_tags: Mapped[list["TaskTag"]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
