"""用户接口响应模型。"""

from pydantic import BaseModel, ConfigDict, Field


# region 用户注册响应
class UserRegisterResponse(BaseModel):
    """注册成功后允许返回给客户端的用户公开信息。"""

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    role: str = Field(..., description="角色")

    # 允许 FastAPI 直接把 SQLAlchemy User 对象转换成该响应模型。
    model_config = ConfigDict(from_attributes=True)


# endregion


# region 用户登录响应
class UserLoginInfo(BaseModel):
    """登录成功后允许返回给客户端的用户公开信息。"""

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    role: str = Field(..., description="角色")


class UserLoginResponse(BaseModel):
    """登录成功后返回的访问令牌和用户公开信息。"""

    # Token 由客户端放入后续请求的 Authorization: Bearer <token> 请求头。
    token: str = Field(..., description="访问令牌")
    # 仅包含前端展示和权限判断需要的公开字段，不包含密码哈希。
    userinfo: UserLoginInfo


# endregion


# region 当前用户信息响应
class UserInfo(BaseModel):
    """用户信息。"""

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    role: str = Field(..., description="角色")
    is_active: bool = Field(..., description="账号是否启用")


# endregion
