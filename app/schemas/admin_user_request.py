"""管理员用户接口请求模型。"""

from pydantic import BaseModel, Field


class AdminUserListRequest(BaseModel):
    """获取用户列表接口接收的分页参数。"""

    # page 从 1 开始，page_size 设置上限可防止管理员一次读取过多用户。
    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页条数")


__all__ = ["AdminUserListRequest"]
