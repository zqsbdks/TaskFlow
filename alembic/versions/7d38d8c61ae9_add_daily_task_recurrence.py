"""增加任务每日重复配置。

Revision ID: 7d38d8c61ae9
Revises: 5c6bf1f552d0
Create Date: 2026-08-31
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "7d38d8c61ae9"
down_revision: str | Sequence[str] | None = "5c6bf1f552d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """为任务增加默认关闭的每日重复开关。"""

    op.add_column(
        "task",
        sa.Column(
            "repeat_daily",
            sa.Boolean(),
            server_default=sa.text("0"),
            nullable=False,
            comment="是否每天重复",
        ),
    )


def downgrade() -> None:
    """移除每日重复开关。"""

    op.drop_column("task", "repeat_daily")
