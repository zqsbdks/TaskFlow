
"""管理员用户接口响应模型。"""

from pydantic import BaseModel, ConfigDict, Field


class AdminUserListItemResponse(BaseModel):
    """用户列表中允许返回给管理员的公开字段。"""

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    role: str = Field(..., description="角色")
    is_active: bool = Field(..., description="是否激活")

    # 允许 Pydantic 直接从 SQLAlchemy User 对象读取响应字段。
    model_config = ConfigDict(from_attributes=True)


class AdminUserListResponse(BaseModel):
    """管理员用户列表及其分页信息。"""

    items: list[AdminUserListItemResponse] = Field(
        default_factory=list,
        description="当前页用户",
    )
    total: int = Field(..., description="用户总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    total_pages: int = Field(..., description="总页数")


__all__ = ["AdminUserListItemResponse", "AdminUserListResponse"]
