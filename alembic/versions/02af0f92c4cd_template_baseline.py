"""模板迁移基线。

Revision ID: 02af0f92c4cd
Revises:
Create Date: 2026-08-23

基础模板尚未包含具体业务 ORM 表，因此本版本不执行 DDL。新项目添加模型后，
应在此基线之上使用 ``alembic revision --autogenerate`` 创建后续迁移。
"""

from collections.abc import Sequence

# 以下标识由 Alembic 构建有向迁移链，revision 在项目内必须唯一。
revision: str = "02af0f92c4cd"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """建立空模板基线；当前没有需要创建的业务表。"""


def downgrade() -> None:
    """回退空模板基线；当前没有需要撤销的 DDL。"""
