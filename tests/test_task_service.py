"""任务 Schema 与 Service 的单元测试。"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.models.task import Task
from app.models.user import User
from app.schemas.task_request import TaskCreateRequest
from app.services import task as task_service


def build_user() -> User:
    """构造无需连接数据库的测试用户对象。"""

    return User(
        id=1,
        username="task-user",
        email="task@example.com",
        password_hash="stored-password-hash",
        role="user",
        is_active=True,
    )


def build_task() -> Task:
    """构造创建成功后的测试任务对象。"""

    now = datetime(2026, 8, 27, 12, 0, 0)
    return Task(
        id=1,
        user_id=1,
        title="完成任务接口",
        description="实现创建任务功能",
        status="pending",
        priority=3,
        due_date=None,
        completed_at=None,
        created_at=now,
        updated_at=now,
    )


# region 任务创建 Service 测试
@pytest.mark.asyncio
async def test_create_task_service_creates_task_for_current_user(monkeypatch) -> None:
    """当前用户没有同名任务时，应以该用户主键创建任务。"""

    user = build_user()
    task = build_task()
    get_by_title = AsyncMock(return_value=None)
    create_task = AsyncMock(return_value=task)
    monkeypatch.setattr(task_service, "get_task_by_title", get_by_title)
    monkeypatch.setattr(task_service, "create_task", create_task)

    result = await task_service.create_task_service(
        db=AsyncMock(),
        current_user=user,
        task_data=TaskCreateRequest(
            title=task.title,
            description=task.description,
        ),
    )

    assert result is task
    assert get_by_title.await_args.kwargs["user_id"] == user.id
    assert create_task.await_args.kwargs["user_id"] == user.id
    assert create_task.await_args.kwargs["status"] == "pending"
    assert create_task.await_args.kwargs["priority"] == 3


@pytest.mark.asyncio
async def test_create_task_service_rejects_duplicate_title(monkeypatch) -> None:
    """当前用户已有同名任务时应返回 409，且不能再次创建。"""

    existing_task = build_task()
    create_task = AsyncMock()
    monkeypatch.setattr(
        task_service,
        "get_task_by_title",
        AsyncMock(return_value=existing_task),
    )
    monkeypatch.setattr(task_service, "create_task", create_task)

    with pytest.raises(HTTPException) as exc_info:
        await task_service.create_task_service(
            db=AsyncMock(),
            current_user=build_user(),
            task_data=TaskCreateRequest(title=existing_task.title),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "任务标题已存在"
    create_task.assert_not_awaited()


# endregion


# region 任务创建请求测试
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "todo"),
        ("priority", 0),
        ("priority", 6),
    ],
)
def test_task_create_request_rejects_invalid_database_values(field: str, value: object) -> None:
    """状态和优先级不符合数据库约束时，应在进入 Router 前被拒绝。"""

    with pytest.raises(ValidationError):
        TaskCreateRequest(title="测试任务", **{field: value})  # type: ignore[arg-type]


# endregion
