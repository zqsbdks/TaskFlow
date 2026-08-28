"""通过 TestClient 验证应用工厂、基础路由和统一响应格式。"""

from fastapi.testclient import TestClient

from app.main import create_app


def test_root() -> None:
    """根路径应返回标准成功响应和欢迎信息。"""

    # client：用于在进程内调用 ASGI 应用的同步测试客户端。
    # 上下文管理器会触发与真实服务器一致的 lifespan 启动和关闭流程。
    with TestClient(create_app()) as client:
        # response：访问根路径后得到的 HTTP 响应，用于验证状态码和统一响应体。
        response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "code": 200,
        "message": "success",
        "data": {"message": "Hello World"},
    }


def test_health() -> None:
    """健康检查应返回 HTTP 200 和可机器识别的 ok 状态。"""

    # client：为本用例单独创建的测试客户端，退出上下文时自动关闭应用资源。
    with TestClient(create_app()) as client:
        # response：健康检查接口返回的 HTTP 响应。
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["data"] == {"status": "ok"}


def test_not_found_uses_standard_response() -> None:
    """不存在的路径也应经过全局异常处理器统一包装。"""

    # client：用于模拟访问不存在路径的测试客户端。
    with TestClient(create_app()) as client:
        # response：不存在路径返回的响应，应由全局异常处理器统一包装。
        response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "message": "Not Found",
        "data": None,
    }


def test_task_router_is_registered() -> None:
    """应用生成的 OpenAPI 文档中应包含创建任务接口。"""

    with TestClient(create_app()) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/tasks/create" in response.json()["paths"]
    assert "/api/v1/tasks/detail/{task_id}" in response.json()["paths"]
    assert "/api/v1/tasks/list" in response.json()["paths"]
    assert "put" in response.json()["paths"]["/api/v1/tasks/update/{task_id}"]
    assert "put" in response.json()["paths"]["/api/v1/tasks/status/{task_id}"]
    assert "delete" in response.json()["paths"]["/api/v1/tasks/delete/{task_id}"]
    assert "/api/v1/tags/create" in response.json()["paths"]
    assert "/api/v1/tags/list" in response.json()["paths"]
