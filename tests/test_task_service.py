"""任务 Schema 与 Service 的单元测试。"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.models.task import Task
from app.models.user import User
from app.schemas.task_request import (
    TaskCreateRequest,
    TaskListRequest,
    TaskStatusUpdateRequest,
    TaskUpdateRequest,
)
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
        repeat_daily=False,
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
    assert create_task.await_args.kwargs["repeat_daily"] is False


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


# region 任务删除 Service 测试
@pytest.mark.asyncio
async def test_delete_task_service_deletes_current_user_task(monkeypatch) -> None:
    """任务存在且属于当前用户时，应调用 CRUD 删除任务。"""

    task = build_task()
    delete_task = AsyncMock()
    monkeypatch.setattr(task_service, "get_task_by_id", AsyncMock(return_value=task))
    monkeypatch.setattr(task_service, "delete_task", delete_task)

    await task_service.delete_task_service(
        db=AsyncMock(),
        current_user=build_user(),
        task_id=task.id,
    )

    delete_task.assert_awaited_once()
    assert delete_task.await_args.kwargs["task"] is task


@pytest.mark.asyncio
async def test_delete_task_service_rejects_missing_task(monkeypatch) -> None:
    """任务不存在或不属于当前用户时，应返回 404 且不能执行删除。"""

    delete_task = AsyncMock()
    monkeypatch.setattr(task_service, "get_task_by_id", AsyncMock(return_value=None))
    monkeypatch.setattr(task_service, "delete_task", delete_task)

    with pytest.raises(HTTPException) as exc_info:
        await task_service.delete_task_service(
            db=AsyncMock(),
            current_user=build_user(),
            task_id=999,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "任务不存在"
    delete_task.assert_not_awaited()


# endregion


# region 任务更新 Service 测试
@pytest.mark.asyncio
async def test_update_task_service_only_updates_submitted_fields(monkeypatch) -> None:
    """部分更新时，不应把请求中未提交的字段覆盖为 None。"""

    task = build_task()
    update_task = AsyncMock(return_value=task)
    monkeypatch.setattr(task_service, "get_task_by_id", AsyncMock(return_value=task))
    monkeypatch.setattr(task_service, "update_task", update_task)

    result = await task_service.update_task_service(
        db=AsyncMock(),
        current_user=build_user(),
        task_id=task.id,
        update_data=TaskUpdateRequest(description="新的任务描述"),
    )

    assert result is task
    assert update_task.await_args.kwargs["update_values"] == {"description": "新的任务描述"}


@pytest.mark.asyncio
async def test_update_task_service_rejects_empty_request(monkeypatch) -> None:
    """请求体没有任何更新字段时，应返回 400。"""

    task = build_task()
    update_task = AsyncMock()
    monkeypatch.setattr(task_service, "get_task_by_id", AsyncMock(return_value=task))
    monkeypatch.setattr(task_service, "update_task", update_task)

    with pytest.raises(HTTPException) as exc_info:
        await task_service.update_task_service(
            db=AsyncMock(),
            current_user=build_user(),
            task_id=task.id,
            update_data=TaskUpdateRequest(),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "没有提供需要更新的字段"
    update_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_task_service_rejects_missing_task(monkeypatch) -> None:
    """任务不存在或不属于当前用户时，应返回 404。"""

    monkeypatch.setattr(task_service, "get_task_by_id", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc_info:
        await task_service.update_task_service(
            db=AsyncMock(),
            current_user=build_user(),
            task_id=999,
            update_data=TaskUpdateRequest(title="新的任务标题"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "没有找到任务"


# endregion


# region 任务状态更新 Service 测试
@pytest.mark.asyncio
async def test_update_task_status_service_sets_completed_time(monkeypatch) -> None:
    """任务改为已完成时，应同时保存状态和完成时间。"""

    task = build_task()
    update_status = AsyncMock(return_value=task)
    monkeypatch.setattr(task_service, "get_task_by_id", AsyncMock(return_value=task))
    monkeypatch.setattr(task_service, "update_task_status", update_status)

    result = await task_service.update_task_status_service(
        db=AsyncMock(),
        current_user=build_user(),
        task_id=task.id,
        status_data=TaskStatusUpdateRequest(status="completed"),
    )

    assert result is task
    assert update_status.await_args.kwargs["status_value"] == "completed"
    assert isinstance(update_status.await_args.kwargs["completed_at"], datetime)


@pytest.mark.asyncio
async def test_update_task_status_service_clears_completed_time(monkeypatch) -> None:
    """任务改为非完成状态时，应清空原来的完成时间。"""

    task = build_task()
    task.status = "completed"
    task.completed_at = datetime(2026, 8, 27, 12, 0, 0)
    update_status = AsyncMock(return_value=task)
    monkeypatch.setattr(task_service, "get_task_by_id", AsyncMock(return_value=task))
    monkeypatch.setattr(task_service, "update_task_status", update_status)

    await task_service.update_task_status_service(
        db=AsyncMock(),
        current_user=build_user(),
        task_id=task.id,
        status_data=TaskStatusUpdateRequest(status="in_progress"),
    )

    assert update_status.await_args.kwargs["status_value"] == "in_progress"
    assert update_status.await_args.kwargs["completed_at"] is None


@pytest.mark.asyncio
async def test_update_task_status_service_creates_next_daily_task(monkeypatch) -> None:
    """每日重复任务完成时，应保留当前记录并生成下一天的任务。"""

    task = build_task()
    task.repeat_daily = True
    task.due_date = datetime(2026, 8, 31, 9, 0, 0)
    complete_recurring = AsyncMock(return_value=task)
    update_status = AsyncMock()
    monkeypatch.setattr(task_service, "get_task_by_id", AsyncMock(return_value=task))
    monkeypatch.setattr(task_service, "complete_recurring_task", complete_recurring)
    monkeypatch.setattr(task_service, "update_task_status", update_status)

    result = await task_service.update_task_status_service(
        db=AsyncMock(),
        current_user=build_user(),
        task_id=task.id,
        status_data=TaskStatusUpdateRequest(status="completed"),
    )

    assert result is task
    assert complete_recurring.await_args.kwargs["next_due_date"] == datetime(
        2026, 9, 1, 9, 0, 0
    )
    update_status.assert_not_awaited()


def test_task_requests_accept_daily_repeat_setting() -> None:
    """创建和编辑请求都应接受每日重复配置。"""

    assert TaskCreateRequest(title="晨间复盘", repeat_daily=True).repeat_daily is True
    assert TaskUpdateRequest(repeat_daily=False).model_dump(exclude_unset=True) == {
        "repeat_daily": False
    }


@pytest.mark.asyncio
async def test_update_task_status_service_rejects_unchanged_status(monkeypatch) -> None:
    """新旧状态相同时应返回 400，且不能写入数据库。"""

    task = build_task()
    update_status = AsyncMock()
    monkeypatch.setattr(task_service, "get_task_by_id", AsyncMock(return_value=task))
    monkeypatch.setattr(task_service, "update_task_status", update_status)

    with pytest.raises(HTTPException) as exc_info:
        await task_service.update_task_status_service(
            db=AsyncMock(),
            current_user=build_user(),
            task_id=task.id,
            status_data=TaskStatusUpdateRequest(status=task.status),
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "任务状态未改变"
    update_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_task_status_service_rejects_missing_task(monkeypatch) -> None:
    """任务不存在或不属于当前用户时，应返回 404。"""

    monkeypatch.setattr(task_service, "get_task_by_id", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc_info:
        await task_service.update_task_status_service(
            db=AsyncMock(),
            current_user=build_user(),
            task_id=999,
            status_data=TaskStatusUpdateRequest(status="completed"),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "任务不存在"


# endregion


# region 任务详情 Service 测试
@pytest.mark.asyncio
async def test_get_task_detail_service_returns_current_user_task(monkeypatch) -> None:
    """任务存在且属于当前用户时，应返回对应任务对象。"""

    user = build_user()
    task = build_task()
    get_task_by_id = AsyncMock(return_value=task)
    monkeypatch.setattr(task_service, "get_task_by_id", get_task_by_id)

    result = await task_service.get_task_detail_service(
        db=AsyncMock(),
        current_user=user,
        task_id=task.id,
    )

    assert result is task
    assert get_task_by_id.await_args.kwargs["task_id"] == task.id
    assert get_task_by_id.await_args.kwargs["user_id"] == user.id


@pytest.mark.asyncio
async def test_get_task_detail_service_rejects_missing_task(monkeypatch) -> None:
    """任务不存在或不属于当前用户时，应返回 404。"""

    monkeypatch.setattr(task_service, "get_task_by_id", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc_info:
        await task_service.get_task_detail_service(
            db=AsyncMock(),
            current_user=build_user(),
            task_id=999,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "没有找到任务"


# endregion


# region 任务列表 Service 测试
@pytest.mark.asyncio
async def test_get_task_list_service_returns_pagination_data(monkeypatch) -> None:
    """列表服务应计算偏移量和总页数，并仅查询当前用户的数据。"""

    user = build_user()
    task = build_task()
    get_task_list = AsyncMock(return_value=([task], 5))
    monkeypatch.setattr(task_service, "get_task_list", get_task_list)

    result = await task_service.get_task_list_service(
        db=AsyncMock(),
        current_user=user,
        query=TaskListRequest(
            page=2,
            page_size=2,
            status="pending",
            priority=3,
        ),
    )

    assert result["items"] == [task]
    assert result["total"] == 5
    assert result["page"] == 2
    assert result["page_size"] == 2
    assert result["total_pages"] == 3
    query_arguments = get_task_list.await_args.kwargs
    assert query_arguments["user_id"] == user.id
    assert query_arguments["offset"] == 2
    assert query_arguments["limit"] == 2
    assert query_arguments["task_status"] == "pending"
    assert query_arguments["priority"] == 3


@pytest.mark.asyncio
async def test_get_task_list_service_handles_empty_result(monkeypatch) -> None:
    """没有符合条件的任务时，应返回空列表和零页。"""

    monkeypatch.setattr(task_service, "get_task_list", AsyncMock(return_value=([], 0)))

    result = await task_service.get_task_list_service(
        db=AsyncMock(),
        current_user=build_user(),
        query=TaskListRequest(),
    )

    assert result["items"] == []
    assert result["total"] == 0
    assert result["total_pages"] == 0


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
