"""任务接口请求模型。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# region 任务创建请求
class TaskCreateRequest(BaseModel):
    """创建任务接口接收的任务内容。"""

    # 字段取值与 Task ORM 模型及数据库检查约束保持一致。
    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    description: str | None = Field(default=None, max_length=200, description="任务描述")
    status: Literal["pending", "in_progress", "completed", "cancelled"] = Field(
        default="pending",
        description="任务状态",
    )
    priority: int = Field(default=3, ge=1, le=5, description="任务优先级（1-5）")
    due_date: datetime | None = Field(default=None, description="任务截止时间")


# endregion


__all__ = ["TaskCreateRequest"]
