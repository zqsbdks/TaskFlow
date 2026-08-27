"""任务接口响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# region 任务创建响应
class TaskCreateResponse(BaseModel):
    """任务创建成功后允许返回给客户端的公开字段。"""

    id: int = Field(..., description="任务ID")
    user_id: int = Field(..., description="所属用户ID")
    title: str = Field(..., description="任务标题")
    description: str | None = Field(default=None, description="任务描述")
    status: str = Field(..., description="任务状态")
    priority: int = Field(..., description="任务优先级（1-5）")
    due_date: datetime | None = Field(default=None, description="任务截止时间")
    completed_at: datetime | None = Field(default=None, description="任务完成时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    # 允许 Pydantic 直接从 SQLAlchemy Task 对象读取响应字段。
    model_config = ConfigDict(from_attributes=True)


# endregion


__all__ = ["TaskCreateResponse"]
