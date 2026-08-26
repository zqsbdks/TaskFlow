"""用户接口请求模型。"""

from pydantic import BaseModel, EmailStr, Field


# region 用户注册请求
class UserRegisterRequest(BaseModel):
    """注册接口接收的用户输入。

    Pydantic 会在进入 Router 前检查字段类型、长度以及邮箱格式。
    """

    # username 和 password 的长度限制用于尽早拒绝超过数据库约束的输入。
    username: str = Field(..., max_length=50, description="用户名")
    email: EmailStr = Field(..., max_length=255, description="邮箱")
    password: str = Field(..., max_length=50, description="密码")


# endregion


# region 用户登录请求
class UserLoginRequest(BaseModel):
    """登录接口接收的邮箱和明文密码。"""

    email: EmailStr = Field(..., max_length=255, description="邮箱")
    password: str = Field(..., max_length=50, description="密码")


# endregion


# region 用户信息更新请求
class UserUpdateRequest(BaseModel):
    """用户更新接口接收的用户输入。

    Pydantic 会在进入 Router 前检查字段类型、长度以及邮箱格式。
    """

    # 两个字段均为可选值，客户端可以只提交本次需要修改的字段。
    username: str | None = Field(default=None, max_length=50, description="用户名")
    email: EmailStr | None = Field(
        default=None,
        max_length=255,
        description="邮箱",
    )


# endregion


# region 用户密码更新请求
class UserPasswordUpdateRequest(BaseModel):
    """修改密码接口接收的旧密码和新密码。"""

    # Python 内部统一使用蛇形命名；新密码至少需要 8 个字符。
    old_password: str = Field(..., min_length=1, max_length=50, description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=50, description="新密码")


# endregion
