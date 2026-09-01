"""任务数据表的 SQLAlchemy ORM 模型。"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.tag import Tag
    from app.models.task_tag import TaskTag
    from app.models.user import User


class Task(Base):
    """保存任务内容、所属用户、状态、优先级和时间信息。"""

    # __tablename__：模型对应的数据库表名。
    __tablename__ = "task"
    # __table_args__：定义状态与优先级约束、常用组合索引及表级中文说明。
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'cancelled')",
            name="valid_status",
        ),
        CheckConstraint("priority BETWEEN 1 AND 5", name="valid_priority"),
        Index("ix_task_user_status", "user_id", "status"),
        Index("ix_task_due_date", "due_date"),
        {
            "comment": "任务信息表",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    # id：自增任务主键，用于唯一标识一条任务。
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="任务主键",
    )
    # user_id：任务所属用户的主键；用户删除时由数据库级联删除其任务。
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
        comment="所属用户主键",
    )
    # title：展示在任务列表中的简短标题，最大长度为 200 个字符。
    title: Mapped[str] = mapped_column(String(200), comment="任务标题")
    # description：可选的任务详细说明，Text 类型适合保存较长内容。
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="任务详细说明",
    )
    # status：任务状态，仅允许待处理、进行中、已完成和已取消四种内部值。
    status: Mapped[str] = mapped_column(
        String(20),
        server_default=text("'pending'"),
        comment="任务状态",
    )
    # priority：任务优先级，1 表示最低、5 表示最高，默认值为 3。
    priority: Mapped[int] = mapped_column(
        SmallInteger,
        server_default=text("3"),
        comment="任务优先级（1-5）",
    )
    # due_date：可选的任务截止时间；为空表示没有明确期限。
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="任务截止时间",
    )
    # repeat_daily：开启后，完成当前任务会自动创建下一天的待办任务。
    repeat_daily: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("0"),
        comment="是否每天重复",
    )
    # completed_at：任务完成时间；尚未完成或重新打开时为空。
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="任务完成时间",
    )
    # created_at：任务记录首次写入数据库的时间。
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("(now())"),
        comment="创建时间",
    )
    # updated_at：任务内容或状态最近一次更新的时间。
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("(now())"),
        onupdate=func.now(),
        comment="更新时间",
    )

    # user：当前任务所属的用户对象。
    user: Mapped["User"] = relationship(back_populates="tasks")
    # task_tags：当前任务与标签之间的全部关联记录。
    task_tags: Mapped[list["TaskTag"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def tags(self) -> list["Tag"]:
        """返回已预加载关联记录中的标签对象。"""

        return [task_tag.tag for task_tag in self.task_tags]
