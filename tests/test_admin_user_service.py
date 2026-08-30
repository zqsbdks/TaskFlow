"""管理员用户 Schema 与 Service 的单元测试。"""

from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.main import create_app
from app.models.user import User
from app.routers import admin_user as admin_user_router_module
from app.schemas.admin_user_request import AdminUpdateRequest, AdminUserListRequest
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


@pytest.mark.asyncio
async def test_update_user_status_service_updates_user_for_admin(monkeypatch) -> None:
    """已启用的管理员应能修改目标用户的启用状态。"""

    target_user = build_user(user_id=2, role="user", is_active=False)
    update_user = AsyncMock(return_value=target_user)
    monkeypatch.setattr(admin_user_service, "update_user", update_user)
    status_data = AdminUpdateRequest(is_active=False)

    result = await admin_user_service.update_user_status_service(
        db=AsyncMock(),
        user_id=target_user.id,
        status=status_data,
        current_user=build_user(),
    )

    assert result is None
    assert update_user.await_args.kwargs["user_id"] == target_user.id
    assert update_user.await_args.kwargs["status"] is status_data


@pytest.mark.asyncio
async def test_update_user_status_service_rejects_missing_user(monkeypatch) -> None:
    """目标用户不存在时应返回 HTTP 404。"""

    monkeypatch.setattr(admin_user_service, "update_user", AsyncMock(return_value=None))

    with pytest.raises(HTTPException) as exc_info:
        await admin_user_service.update_user_status_service(
            db=AsyncMock(),
            user_id=999,
            status=AdminUpdateRequest(is_active=False),
            current_user=build_user(),
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "用户不存在"


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
