"""标签接口响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# region 标签创建响应
class TagCreateResponse(BaseModel):
    """标签创建成功后允许返回给客户端的公开字段。"""

    id: int = Field(..., description="标签ID")
    name: str = Field(..., description="标签名称")
    color: str | None = Field(default=None, description="标签颜色")
    created_at: datetime = Field(..., description="创建时间")

    # 允许 Pydantic 直接从 SQLAlchemy Tag 对象读取响应字段。
    model_config = ConfigDict(from_attributes=True)


# endregion


__all__ = ["TagCreateResponse"]
