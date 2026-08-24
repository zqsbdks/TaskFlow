"""通过 TestClient 验证应用工厂、基础路由和统一响应格式。"""

from fastapi.testclient import TestClient

from app.main import create_app


def test_root() -> None:
    """根路径应返回标准成功响应和欢迎信息。"""

    # 上下文管理器会触发与真实服务器一致的 lifespan 启动和关闭流程。
    with TestClient(create_app()) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "code": 200,
        "message": "success",
        "data": {"message": "Hello World"},
    }


def test_health() -> None:
    """健康检查应返回 HTTP 200 和可机器识别的 ok 状态。"""

    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["data"] == {"status": "ok"}


def test_not_found_uses_standard_response() -> None:
    """不存在的路径也应经过全局异常处理器统一包装。"""

    with TestClient(create_app()) as client:
        response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "message": "Not Found",
        "data": None,
    }
