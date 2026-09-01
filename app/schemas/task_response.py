"""任务接口响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.tag_response import TagListResponse


# region 任务响应
class TaskCreateResponse(BaseModel):
    """任务创建成功后允许返回给客户端的公开字段。"""

    id: int = Field(..., description="任务ID")
    user_id: int = Field(..., description="所属用户ID")
    title: str = Field(..., description="任务标题")
    description: str | None = Field(default=None, description="任务描述")
    status: str = Field(..., description="任务状态")
    priority: int = Field(..., description="任务优先级（1-5）")
    due_date: datetime | None = Field(default=None, description="任务截止时间")
    repeat_daily: bool = Field(default=False, description="是否每天重复")
    completed_at: datetime | None = Field(default=None, description="任务完成时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    # 允许 Pydantic 直接从 SQLAlchemy Task 对象读取响应字段。
    model_config = ConfigDict(from_attributes=True)


# endregion


# region 任务列表响应
class TaskListItemResponse(TaskCreateResponse):
    """任务列表项，并包含已关联的标签。"""

    tags: list[TagListResponse] = Field(default_factory=list, description="任务标签")


class TaskListResponse(BaseModel):
    """任务列表及其分页信息。"""

    items: list[TaskListItemResponse] = Field(default_factory=list, description="当前页任务")
    total: int = Field(..., description="符合条件的任务总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    total_pages: int = Field(..., description="总页数")


# endregion


# region 任务详情响应
class TaskDetailResponse(BaseModel):
    """任务详情接口允许返回给客户端的公开字段。"""

    id: int = Field(..., description="任务ID")
    title: str = Field(..., description="任务标题")
    description: str | None = Field(default=None, description="任务描述")
    status: str = Field(..., description="任务状态")
    priority: int = Field(..., description="任务优先级（1-5）")
    user_id: int = Field(..., description="任务创建者ID")
    repeat_daily: bool = Field(default=False, description="是否每天重复")

    # 允许 Pydantic 直接从 SQLAlchemy Task 对象读取响应字段。
    model_config = ConfigDict(from_attributes=True)


# endregion


# region 任务更新响应
class TaskUpdateResponse(BaseModel):
    """任务更新接口允许返回给客户端的公开字段。"""

    id: int = Field(..., description="任务ID")
    title: str = Field(..., description="任务标题")
    description: str | None = Field(default=None, description="任务描述")
    status: str = Field(..., description="任务状态")
    priority: int = Field(..., description="任务优先级（1-5）")
    user_id: int = Field(..., description="任务创建者ID")
    due_date: datetime | None = Field(default=None, description="任务截止日期")
    repeat_daily: bool = Field(default=False, description="是否每天重复")
    completed_at: datetime | None = Field(default=None, description="任务完成时间")
    updated_at: datetime = Field(..., description="更新时间")

    # 允许 Pydantic 直接从 SQLAlchemy Task 对象读取响应字段。
    model_config = ConfigDict(from_attributes=True)


# endregion


# region 任务状态更新响应
class TaskStatusUpdateResponse(BaseModel):
    """任务状态更新成功后返回的状态相关字段。"""

    id: int = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    completed_at: datetime | None = Field(default=None, description="任务完成时间")
    updated_at: datetime = Field(..., description="更新时间")

    # 允许 Pydantic 直接从 SQLAlchemy Task 对象读取响应字段。
    model_config = ConfigDict(from_attributes=True)


# endregion


__all__ = [
    "TaskCreateResponse",
    "TaskDetailResponse",
    "TaskListItemResponse",
    "TaskListResponse",
    "TaskStatusUpdateResponse",
    "TaskUpdateResponse",
]
