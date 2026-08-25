"""将标签调整为用户私有资源。

Revision ID: 5c6bf1f552d0
Revises: ea1eaf00d47f
Create Date: 2026-08-25 22:15:08.917097

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# Alembic 使用以下标识构建迁移版本链；生成后不要随意修改 revision。
revision: str = "5c6bf1f552d0"
down_revision: str | Sequence[str] | None = "ea1eaf00d47f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """增加标签所有者，并把标签名唯一性限制在单个用户范围内。"""

    # 离线 SQL 模式没有真实连接；在线升级时才检查是否存在无法自动归属的旧标签。
    if not op.get_context().as_sql:
        # connection：Alembic 当前使用的同步数据库连接。
        connection = op.get_bind()
        # existing_tag_count：升级前已有的旧标签数量；旧结构无法可靠推断标签所有者。
        existing_tag_count = connection.execute(sa.text("SELECT COUNT(*) FROM tag")).scalar_one()
        if existing_tag_count:
            raise RuntimeError(
                "tag 表中已有数据，无法自动确定 user_id；请先为旧标签制定用户归属迁移方案"
            )

    op.add_column(
        "tag",
        sa.Column("user_id", sa.BigInteger(), nullable=False, comment="所属用户主键"),
    )
    op.drop_index(op.f("ix_tag_name"), table_name="tag")
    op.create_index(op.f("ix_tag_user_id"), "tag", ["user_id"], unique=False)
    op.create_unique_constraint("user_name", "tag", ["user_id", "name"])
    op.create_foreign_key(
        op.f("fk_tag_user_id_user"),
        "tag",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """恢复全局唯一标签；存在跨用户同名标签时拒绝不安全回退。"""

    # 离线 SQL 模式没有真实连接；在线回退时才检查全局唯一约束能否安全恢复。
    if not op.get_context().as_sql:
        # connection：Alembic 当前使用的同步数据库连接。
        connection = op.get_bind()
        # duplicate_name_count：跨用户重复使用的标签名称数量。
        duplicate_name_count = connection.execute(
            sa.text(
                "SELECT COUNT(*) FROM ("
                "SELECT name FROM tag GROUP BY name HAVING COUNT(*) > 1"
                ") AS duplicate_names"
            )
        ).scalar_one()
        if duplicate_name_count:
            raise RuntimeError("存在跨用户同名标签，无法恢复标签名称全局唯一约束")

    op.drop_constraint(op.f("fk_tag_user_id_user"), "tag", type_="foreignkey")
    op.drop_constraint("user_name", "tag", type_="unique")
    op.drop_index(op.f("ix_tag_user_id"), table_name="tag")
    op.create_index(op.f("ix_tag_name"), "tag", ["name"], unique=True)
    op.drop_column("tag", "user_id")
