"""管理员用户 Schema、Service 与 Router 的单元测试。"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.main import create_app
from app.models.task import Task
from app.models.user import User
from app.routers import admin_user as admin_user_router_module
from app.schemas.admin_user_request import (
    AdminTaskListRequest,
    AdminUpdateRequest,
    AdminUserListRequest,
)
from app.schemas.admin_user_response import (
    AdminUserListItemResponse,
    AdminUserListResponse,
)
from app.schemas.base import ResponseModel
from app.services import admin_user as admin_user_service


def build_user(
    *,
    user_id: int = 1,
    role: str = "admin",
    is_active: bool = True,
) -> User:
    """构造无需连接数据库的测试用户对象。"""

    return User(
        id=user_id,
        username=f"user-{user_id}",
        email=f"user-{user_id}@example.com",
        password_hash="stored-password-hash",
        role=role,
        is_active=is_active,
    )


def build_task(*, task_id: int = 1, user_id: int = 2) -> Task:
    """构造无需连接数据库的测试任务对象。"""

    now = datetime(2026, 8, 30, 12, 0, 0)
    return Task(
        id=task_id,
        user_id=user_id,
        title=f"任务-{task_id}",
        description=None,
        status="pending",
        priority=3,
        due_date=None,
        repeat_daily=False,
        completed_at=None,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_get_user_lists_service_returns_all_users_for_admin(monkeypatch) -> None:
    """已启用的管理员应取得 CRUD 返回的分页用户列表。"""

    users = [build_user(user_id=2, role="user")]
    get_user_list = AsyncMock(return_value=(users, 3))
    monkeypatch.setattr(admin_user_service, "get_user_list", get_user_list)

    result = await admin_user_service.get_user_lists_service(
        db=AsyncMock(),
        current_user=build_user(),
        query=AdminUserListRequest(page=2, page_size=2),
    )

    assert result["items"] == users
    assert result["total"] == 3
    assert result["page"] == 2
    assert result["page_size"] == 2
    assert result["total_pages"] == 2
    assert get_user_list.await_args.kwargs["offset"] == 2
    assert get_user_list.await_args.kwargs["limit"] == 2


@pytest.mark.asyncio
async def test_get_user_lists_service_rejects_non_admin(monkeypatch) -> None:
    """普通用户访问用户列表时应返回 403，且不执行数据库查询。"""

    get_user_list = AsyncMock()
    monkeypatch.setattr(admin_user_service, "get_user_list", get_user_list)

    with pytest.raises(HTTPException) as exc_info:
        await admin_user_service.get_user_lists_service(
            db=AsyncMock(),
            current_user=build_user(role="user"),
            query=AdminUserListRequest(),
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "无权限访问"
    get_user_list.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_user_lists_service_rejects_inactive_admin(monkeypatch) -> None:
    """已禁用的管理员访问用户列表时应返回 403。"""

    get_user_list = AsyncMock()
    monkeypatch.setattr(admin_user_service, "get_user_list", get_user_list)

    with pytest.raises(HTTPException) as exc_info:
        await admin_user_service.get_user_lists_service(
            db=AsyncMock(),
            current_user=build_user(is_active=False),
            query=AdminUserListRequest(),
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "用户已被禁用"
    get_user_list.assert_not_awaited()


def test_admin_user_list_response_serializes_orm_users() -> None:
    """分页响应模型应包含用户条目和完整分页信息。"""

    users = [build_user(user_id=1), build_user(user_id=2, role="user")]
    items = [AdminUserListItemResponse.model_validate(user) for user in users]

    response = ResponseModel[AdminUserListResponse](
        message="获取用户列表成功",
        data=AdminUserListResponse(
            items=items,
            total=2,
            page=1,
            page_size=10,
            total_pages=1,
        ),
    )

    assert response.data is not None
    assert [user.id for user in response.data.items] == [1, 2]
    assert response.data.items[1].role == "user"
    assert response.data.total_pages == 1


def test_admin_user_list_route_serializes_response(monkeypatch) -> None:
    """真实路由响应应通过 FastAPI 校验并返回用户对象列表。"""

    users = [build_user(user_id=1), build_user(user_id=2, role="user")]
    paginated_users = {
        "items": users,
        "total": 2,
        "page": 1,
        "page_size": 10,
        "total_pages": 1,
    }
    get_user_lists_service = AsyncMock(return_value=paginated_users)
    monkeypatch.setattr(
        admin_user_router_module,
        "get_user_lists_service",
        get_user_lists_service,
    )

    application = create_app()
    application.dependency_overrides[get_db] = lambda: AsyncMock()
    application.dependency_overrides[get_current_user] = lambda: users[0]

    with TestClient(application) as client:
        response = client.get("/api/v1/admin/user/list?page=1&page_size=10")

    assert response.status_code == 200
    assert response.json() == {
        "code": 200,
        "message": "获取用户列表成功",
        "data": {
            "items": [
                {
                    "id": 1,
                    "username": "user-1",
                    "email": "user-1@example.com",
                    "role": "admin",
                    "is_active": True,
                },
                {
                    "id": 2,
                    "username": "user-2",
                    "email": "user-2@example.com",
                    "role": "user",
                    "is_active": True,
                },
            ],
            "total": 2,
            "page": 1,
            "page_size": 10,
            "total_pages": 1,
        },
    }


# region 管理员任务列表测试
@pytest.mark.asyncio
async def test_get_all_task_list_service_returns_paginated_tasks(monkeypatch) -> None:
    """已启用的管理员应取得所有用户的分页任务列表。"""

    tasks = [build_task(task_id=3, user_id=2)]
    get_all_task_list = AsyncMock(return_value=(tasks, 5))
    monkeypatch.setattr(admin_user_service, "get_all_task_list", get_all_task_list)

    result = await admin_user_service.get_all_task_list_service(
        db=AsyncMock(),
        current_user=build_user(),
        query=AdminTaskListRequest(page=2, page_size=2),
    )

    assert result["items"] == tasks
    assert result["total"] == 5
    assert result["page"] == 2
    assert result["page_size"] == 2
    assert result["total_pages"] == 3
    assert get_all_task_list.await_args.kwargs["offset"] == 2
    assert get_all_task_list.await_args.kwargs["limit"] == 2


@pytest.mark.asyncio
async def test_get_all_task_list_service_rejects_non_admin(monkeypatch) -> None:
    """普通用户访问全部任务列表时应返回 403，且不执行查询。"""

    get_all_task_list = AsyncMock()
    monkeypatch.setattr(admin_user_service, "get_all_task_list", get_all_task_list)

    with pytest.raises(HTTPException) as exc_info:
        await admin_user_service.get_all_task_list_service(
            db=AsyncMock(),
            current_user=build_user(role="user"),
            query=AdminTaskListRequest(),
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "无权限访问"
    get_all_task_list.assert_not_awaited()


def test_get_all_task_list_route_serializes_response(monkeypatch) -> None:
    """管理员任务列表路由应返回任务及完整分页信息。"""

    tasks = [build_task(task_id=3, user_id=2)]
    paginated_tasks = {
        "items": tasks,
        "total": 1,
        "page": 1,
        "page_size": 10,
        "total_pages": 1,
    }
    get_all_task_list_service = AsyncMock(return_value=paginated_tasks)
    monkeypatch.setattr(
        admin_user_router_module,
        "get_all_task_list_service",
        get_all_task_list_service,
    )

    application = create_app()
    application.dependency_overrides[get_db] = lambda: AsyncMock()
    application.dependency_overrides[get_current_user] = lambda: build_user()

    with TestClient(application) as client:
        response = client.get("/api/v1/admin/user/task/list?page=1&page_size=10")

    assert response.status_code == 200
    assert response.json()["message"] == "获取全部任务列表成功"
    assert response.json()["data"]["total"] == 1
    assert response.json()["data"]["items"][0]["id"] == 3
    assert response.json()["data"]["items"][0]["user_id"] == 2


# endregion


@pytest.mark.asyncio
async def test_update_user_status_service_updates_user_for_admin(monkeypatch) -> None:
    """已启用的管理员应能修改目标用户的启用状态。"""

    target_user = build_user(user_id=2, role="user", is_active=False)
    update_user = AsyncMock(return_value=target_user)
    monkeypatch.setattr(
        admin_user_service,
        "get_user_by_id",
        AsyncMock(return_value=target_user),
    )
    monkeypatch.setattr(admin_user_service, "update_user", update_user)
    status_data = AdminUpdateRequest(is_active=False)

    result = await admin_user_service.update_user_status_service(
        db=AsyncMock(),
        user_id=target_user.id,
        status=status_data,
        current_user=build_user(),
    )

    assert result is None
    assert update_user.await_args.kwargs["user"] is target_user
    assert update_user.await_args.kwargs["is_active"] is False


@pytest.mark.asyncio
async def test_update_user_status_service_rejects_missing_user(monkeypatch) -> None:
    """目标用户不存在时应返回 HTTP 404。"""

    get_user_by_id = AsyncMock(return_value=None)
    update_user = AsyncMock()
    monkeypatch.setattr(admin_user_service, "get_user_by_id", get_user_by_id)
    monkeypatch.setattr(admin_user_service, "update_user", update_user)

    with pytest.raises(HTTPException) as exc_info:
        await admin_user_service.update_user_status_service(
            db=AsyncMock(),
            user_id=999,
            status=AdminUpdateRequest(is_active=False),
            current_user=build_user(),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "用户不存在"
    update_user.assert_not_awaited()


def test_update_user_status_route_returns_success(monkeypatch) -> None:
    """更新接口应接收状态请求体并返回统一成功响应。"""

    update_status = AsyncMock(return_value=None)
    monkeypatch.setattr(
        admin_user_router_module,
        "update_user_status_service",
        update_status,
    )

    application = create_app()
    application.dependency_overrides[get_db] = lambda: AsyncMock()
    application.dependency_overrides[get_current_user] = lambda: build_user()

    with TestClient(application) as client:
        response = client.put(
            "/api/v1/admin/user/status/2",
            json={"is_active": False},
        )

    assert response.status_code == 200
    assert response.json() == {
        "code": 200,
        "message": "更新用户状态成功",
        "data": None,
    }
    assert update_status.await_args.kwargs["user_id"] == 2
    assert not update_status.await_args.kwargs["status"].is_active


@pytest.mark.asyncio
async def test_delete_user_service_deletes_user_for_admin(monkeypatch) -> None:
    """已启用的管理员应能删除存在的目标用户。"""

    target_user = build_user(user_id=2, role="user")
    get_user_by_id = AsyncMock(return_value=target_user)
    delete_user = AsyncMock(return_value=None)
    monkeypatch.setattr(admin_user_service, "get_user_by_id", get_user_by_id)
    monkeypatch.setattr(admin_user_service, "delete_user", delete_user)
    db = AsyncMock()

    result = await admin_user_service.delete_user_service(
        db=db,
        user_id=target_user.id,
        current_user=build_user(),
    )

    assert result is None
    delete_user.assert_awaited_once_with(db=db, user=target_user)


@pytest.mark.asyncio
async def test_delete_user_service_rejects_missing_user(monkeypatch) -> None:
    """删除不存在的用户时应返回 HTTP 404，且不执行删除。"""

    delete_user = AsyncMock()
    monkeypatch.setattr(
        admin_user_service,
        "get_user_by_id",
        AsyncMock(return_value=None),
    )
    monkeypatch.setattr(admin_user_service, "delete_user", delete_user)

    with pytest.raises(HTTPException) as exc_info:
        await admin_user_service.delete_user_service(
            db=AsyncMock(),
            user_id=999,
            current_user=build_user(),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "用户不存在"
    delete_user.assert_not_awaited()


def test_delete_user_route_returns_success(monkeypatch) -> None:
    """删除接口应调用 Service 并返回统一成功响应。"""

    delete_service = AsyncMock(return_value=None)
    monkeypatch.setattr(
        admin_user_router_module,
        "delete_user_service",
        delete_service,
    )

    application = create_app()
    application.dependency_overrides[get_db] = lambda: AsyncMock()
    application.dependency_overrides[get_current_user] = lambda: build_user()

    with TestClient(application) as client:
        response = client.delete("/api/v1/admin/user/delete/2")

    assert response.status_code == 200
    assert response.json() == {
        "code": 200,
        "message": "删除用户成功",
        "data": None,
    }
    assert delete_service.await_args.kwargs["user_id"] == 2
