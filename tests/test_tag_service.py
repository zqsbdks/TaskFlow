"""标签 Schema 与 Service 的单元测试。"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.models.tag import Tag
from app.models.task import Task
from app.models.task_tag import TaskTag
from app.models.user import User
from app.schemas.tag_request import TagCreateRequest
from app.services import tag as tag_service


def build_user() -> User:
    """构造无需连接数据库的测试用户对象。"""

    return User(
        id=1,
        username="tag-user",
        email="tag@example.com",
        password_hash="stored-password-hash",
        role="user",
        is_active=True,
    )


def build_tag() -> Tag:
    """构造创建成功后的测试标签对象。"""

    return Tag(
        id=1,
        user_id=1,
        name="后端",
        color="#3B82F6",
        created_at=datetime(2026, 8, 28, 12, 0, 0),
    )


def build_task() -> Task:
    """构造属于测试用户的任务对象。"""

    now = datetime(2026, 8, 28, 12, 0, 0)
    return Task(
        id=1,
        user_id=1,
        title="编写标签接口",
        description=None,
        status="pending",
        priority=3,
        due_date=None,
        completed_at=None,
        created_at=now,
        updated_at=now,
    )


# region 标签创建 Service 测试
@pytest.mark.asyncio
async def test_create_tag_service_creates_tag_for_current_user(monkeypatch) -> None:
    """当前用户没有同名标签时，应以该用户主键创建标签。"""

    user = build_user()
    tag = build_tag()
    get_tag_by_name = AsyncMock(return_value=None)
    create_tag = AsyncMock(return_value=tag)
    monkeypatch.setattr(tag_service, "get_tag_by_name", get_tag_by_name)
    monkeypatch.setattr(tag_service, "create_tag", create_tag)

    result = await tag_service.create_tag_service(
        db=AsyncMock(),
        current_user=user,
        tag_data=TagCreateRequest(name=tag.name, color=tag.color),
    )

    assert result is tag
    assert get_tag_by_name.await_args.kwargs["user_id"] == user.id
    assert create_tag.await_args.kwargs["user_id"] == user.id
    assert create_tag.await_args.kwargs["name"] == tag.name


@pytest.mark.asyncio
async def test_create_tag_service_rejects_duplicate_name(monkeypatch) -> None:
    """当前用户已有同名标签时应返回 409，并且不再创建。"""

    tag = build_tag()
    create_tag = AsyncMock()
    monkeypatch.setattr(tag_service, "get_tag_by_name", AsyncMock(return_value=tag))
    monkeypatch.setattr(tag_service, "create_tag", create_tag)

    with pytest.raises(HTTPException) as exc_info:
        await tag_service.create_tag_service(
            db=AsyncMock(),
            current_user=build_user(),
            tag_data=TagCreateRequest(name=tag.name, color=tag.color),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "标签名称已存在"
    create_tag.assert_not_awaited()


# endregion


# region 为任务添加标签 Service 测试
@pytest.mark.asyncio
async def test_add_tag_for_task_service_creates_relation(monkeypatch) -> None:
    """任务和标签属于当前用户且未绑定时，应创建关联并返回标签。"""

    user = build_user()
    task = build_task()
    tag = build_tag()
    add_tag_to_task = AsyncMock(return_value=TaskTag(task_id=task.id, tag_id=tag.id))
    monkeypatch.setattr(tag_service, "get_task_by_id", AsyncMock(return_value=task))
    monkeypatch.setattr(tag_service, "get_tag_by_id", AsyncMock(return_value=tag))
    monkeypatch.setattr(tag_service, "get_task_tag", AsyncMock(return_value=None))
    monkeypatch.setattr(tag_service, "add_tag_to_task", add_tag_to_task)

    result = await tag_service.add_tag_for_task_service(
        db=AsyncMock(),
        current_user=user,
        task_id=task.id,
        tag_id=tag.id,
    )

    assert result is tag
    assert add_tag_to_task.await_args.kwargs["task_id"] == task.id
    assert add_tag_to_task.await_args.kwargs["tag_id"] == tag.id


@pytest.mark.asyncio
async def test_add_tag_for_task_service_rejects_missing_task(monkeypatch) -> None:
    """当前用户没有指定任务时应返回 404。"""

    get_tag_by_id = AsyncMock()
    monkeypatch.setattr(tag_service, "get_task_by_id", AsyncMock(return_value=None))
    monkeypatch.setattr(tag_service, "get_tag_by_id", get_tag_by_id)

    with pytest.raises(HTTPException) as exc_info:
        await tag_service.add_tag_for_task_service(
            db=AsyncMock(),
            current_user=build_user(),
            task_id=1,
            tag_id=1,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "任务不存在"
    get_tag_by_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_add_tag_for_task_service_rejects_missing_tag(monkeypatch) -> None:
    """当前用户没有指定标签时应返回 404。"""

    monkeypatch.setattr(tag_service, "get_task_by_id", AsyncMock(return_value=build_task()))
    monkeypatch.setattr(tag_service, "get_tag_by_id", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc_info:
        await tag_service.add_tag_for_task_service(
            db=AsyncMock(),
            current_user=build_user(),
            task_id=1,
            tag_id=1,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "标签不存在"


@pytest.mark.asyncio
async def test_add_tag_for_task_service_rejects_duplicate_relation(monkeypatch) -> None:
    """任务已经绑定指定标签时应返回 409，并且不重复写入。"""

    add_tag_to_task = AsyncMock()
    monkeypatch.setattr(tag_service, "get_task_by_id", AsyncMock(return_value=build_task()))
    monkeypatch.setattr(tag_service, "get_tag_by_id", AsyncMock(return_value=build_tag()))
    monkeypatch.setattr(
        tag_service,
        "get_task_tag",
        AsyncMock(return_value=TaskTag(task_id=1, tag_id=1)),
    )
    monkeypatch.setattr(tag_service, "add_tag_to_task", add_tag_to_task)

    with pytest.raises(HTTPException) as exc_info:
        await tag_service.add_tag_for_task_service(
            db=AsyncMock(),
            current_user=build_user(),
            task_id=1,
            tag_id=1,
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "任务已经添加了该标签"
    add_tag_to_task.assert_not_awaited()


# endregion


# region 标签创建请求测试
def test_tag_create_request_rejects_invalid_color() -> None:
    """颜色不是六位十六进制格式时，应在进入 Router 前被拒绝。"""

    with pytest.raises(ValidationError):
        TagCreateRequest(name="后端", color="blue")


# endregion
