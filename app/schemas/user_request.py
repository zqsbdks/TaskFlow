"""用户接口请求模型。"""

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """注册接口接收的用户输入。

    Pydantic 会在进入 Router 前检查字段类型、长度以及邮箱格式。
    """

    # username 和 password 的长度限制用于尽早拒绝超过数据库约束的输入。
    username: str = Field(..., max_length=50, description="用户名")
    email: EmailStr = Field(..., max_length=255, description="邮箱")
    password: str = Field(..., max_length=50, description="密码")
