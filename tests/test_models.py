"""验证 TaskFlow ORM 表结构、关系和数据库约束。"""

from datetime import datetime

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import configure_mappers

from app.models import Base, Tag, Task, TaskTag
from app.schemas.task_response import TaskListItemResponse


def test_all_business_models_are_registered() -> None:
    """四张业务表必须注册到 Alembic 使用的同一份 metadata。"""

    configure_mappers()

    # expected_table_names：TaskFlow 当前约定的完整业务表集合。
    expected_table_names = {"user", "task", "tag", "task_tag"}
    assert set(Base.metadata.tables) == expected_table_names


def test_tag_belongs_to_user_and_name_is_unique_per_user() -> None:
    """标签必须属于用户，且只限制同一用户不能创建重名标签。"""

    # tag_table：标签模型生成的 SQLAlchemy 表元数据。
    tag_table = Base.metadata.tables["tag"]
    # foreign_keys：标签表上声明的全部外键约束。
    foreign_keys = [
        constraint
        for constraint in tag_table.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    ]
    # unique_constraints：标签表上声明的全部唯一约束。
    unique_constraints = [
        constraint
        for constraint in tag_table.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    assert tag_table.c.user_id.nullable is False
    assert len(foreign_keys) == 1
    assert foreign_keys[0].referred_table.name == "user"
    assert foreign_keys[0].ondelete == "CASCADE"
    assert len(unique_constraints) == 1
    assert [column.name for column in unique_constraints[0].columns] == ["user_id", "name"]


def test_timestamp_defaults_match_mysql_reflection() -> None:
    """时间字段默认表达式应与当前 MySQL 反射结果一致，避免虚假迁移。"""

    # timestamp_columns：全部依赖数据库生成当前时间的模型字段。
    timestamp_columns = [
        Base.metadata.tables["user"].c.created_at,
        Base.metadata.tables["user"].c.updated_at,
        Base.metadata.tables["task"].c.created_at,
        Base.metadata.tables["task"].c.updated_at,
        Base.metadata.tables["tag"].c.created_at,
        Base.metadata.tables["task_tag"].c.created_at,
    ]

    for column in timestamp_columns:
        assert column.server_default is not None
        assert str(column.server_default.arg) == "(now())"


def test_task_list_item_serializes_associated_tags() -> None:
    """任务列表项应包含关联标签的名称和颜色。"""

    now = datetime(2026, 8, 31, 12, 0, 0)
    tag = Tag(id=2, user_id=1, name="医院", color="#22C55E", created_at=now)
    task = Task(
        id=3,
        user_id=1,
        title="明天去医院",
        description=None,
        status="pending",
        priority=3,
        due_date=None,
        completed_at=None,
        created_at=now,
        updated_at=now,
    )
    task.task_tags = [TaskTag(task_id=task.id, tag_id=tag.id, tag=tag)]

    response = TaskListItemResponse.model_validate(task)

    assert [(item.name, item.color) for item in response.tags] == [("医院", "#22C55E")]
