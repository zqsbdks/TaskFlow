"""用户接口响应模型。"""

from pydantic import BaseModel, ConfigDict, Field


class UserRegisterResponse(BaseModel):
    """注册成功后允许返回给客户端的用户公开信息。"""

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    role: str = Field(..., description="角色")

    # 允许 FastAPI 直接把 SQLAlchemy User 对象转换成该响应模型。
    model_config = ConfigDict(from_attributes=True)
