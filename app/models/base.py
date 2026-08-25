"""SQLAlchemy 声明式基类。

所有 ORM 模型必须继承同一个 ``Base``，以便 Alembic 一次读取完整元数据。
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# naming_convention：为主键、外键、索引和约束生成稳定名称，避免 Alembic
# 在不同开发环境中生成名称不一致的迁移脚本。
naming_convention = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """项目内所有 ORM 实体共用的声明式基类。

    业务模型必须继承本类，不能各自创建新的 ``DeclarativeBase``，否则 Alembic
    无法从一份 ``metadata`` 中发现所有表。
    """

    # metadata：集中保存四张业务表的结构，并应用统一的约束命名规则。
    metadata = MetaData(naming_convention=naming_convention)
