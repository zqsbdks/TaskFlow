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


# region 任务列表查询请求
class TaskListRequest(BaseModel):
    """获取任务列表接口接收的分页和筛选条件。"""

    # page 从 1 开始，page_size 设置上限可防止单次读取过多数据。
    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页条数")
    # None 表示不按该字段筛选，因此默认返回当前用户的全部任务。
    status: Literal["pending", "in_progress", "completed", "cancelled"] | None = Field(
        default=None,
        description="任务状态",
    )
    priority: int | None = Field(default=None, ge=1, le=5, description="任务优先级（1-5）")


# endregion


__all__ = ["TaskCreateRequest", "TaskListRequest"]
