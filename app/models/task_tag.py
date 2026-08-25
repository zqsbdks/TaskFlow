"""任务与标签多对多关联表的 SQLAlchemy ORM 模型。"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.tag import Tag
    from app.models.task import Task


class TaskTag(Base):
    """保存任务和标签的绑定关系，并通过联合主键防止重复绑定。"""

    # __tablename__：模型对应的数据库关联表名称。
    __tablename__ = "task_tag"
    # __table_args__：设置表级中文说明和统一字符集。
    __table_args__ = {
        "comment": "任务与标签关联表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    # task_id：关联的任务主键，同时构成联合主键的一部分。
    task_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("task.id", ondelete="CASCADE"),
        primary_key=True,
        comment="任务主键",
    )
    # tag_id：关联的标签主键，同时构成联合主键的一部分。
    tag_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
        comment="标签主键",
    )
    # created_at：任务与标签建立绑定关系的时间。
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("(now())"),
        comment="关联创建时间",
    )

    # task：当前关联记录指向的任务对象。
    task: Mapped["Task"] = relationship(back_populates="task_tags")
    # tag：当前关联记录指向的标签对象。
    tag: Mapped["Tag"] = relationship(back_populates="task_tags")
