"""任务 API 路由。"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.schemas.base import ResponseModel
from app.schemas.task_request import TaskCreateRequest, TaskListRequest, TaskUpdateRequest
from app.schemas.task_response import (
    TaskCreateResponse,
    TaskDetailResponse,
    TaskListResponse,
    TaskUpdateResponse,
)
from app.services.task import (
    create_task_service,
    get_task_detail_service,
    get_task_list_service,
    update_task_service,
)

# 任务领域接口统一使用 /tasks 路径前缀和中文 Swagger 标签。
task_router = APIRouter(tags=["任务"], prefix="/tasks")


# region 任务创建
@task_router.post(
    "/create",
    response_model=ResponseModel[TaskCreateResponse],
)
async def create_task(
    task_data: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """为当前登录用户创建任务并返回任务详情。"""

    # Router 只负责输入输出，重复检查及创建流程统一交给 Service。
    new_task = await create_task_service(
        db=db,
        current_user=current_user,
        task_data=task_data,
    )

    # TaskCreateResponse 会从 ORM 对象读取并筛选允许公开的任务字段。
    return ResponseModel(
        message="创建任务成功",
        data=new_task,
    )


# endregion


# region 任务列表
@task_router.get("/list", response_model=ResponseModel[TaskListResponse])
async def get_task_list(
    query: Annotated[TaskListRequest, Query()],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分页获取当前登录用户的任务，并支持状态和优先级筛选。"""

    # GET 查询参数由 TaskListRequest 校验，列表查询和分页计算交给 Service。
    task_list = await get_task_list_service(
        db=db,
        current_user=current_user,
        query=query,
    )

    return ResponseModel(code=200, message="获取任务列表成功", data=task_list)


# endregion


# region 任务详情
@task_router.get("/detail/{task_id}", response_model=ResponseModel[TaskDetailResponse])
async def get_task_detail(
    task_id: int = Path(..., ge=1, description="任务ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前登录用户拥有的指定任务详情。"""

    # Service 负责确认任务存在且属于当前用户。
    task_data = await get_task_detail_service(
        task_id=task_id,
        db=db,
        current_user=current_user,
    )

    # TaskDetailResponse 会从 ORM 对象读取并筛选允许公开的字段。
    return ResponseModel(
        message="获取任务详情成功",
        data=task_data,
    )


# endregion


# region 任务更新
@task_router.put("/update/{task_id}", response_model=ResponseModel[TaskUpdateResponse])
async def update_task(
    update_data: TaskUpdateRequest,
    task_id: int = Path(..., ge=1, description="任务ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户拥有的任务，仅修改请求体中实际提交的字段。"""

    # Service 负责权限检查、业务校验、完成时间处理和数据库更新。
    task = await update_task_service(
        task_id=task_id,
        db=db,
        current_user=current_user,
        update_data=update_data,
    )

    # TaskUpdateResponse 会从更新后的 ORM 对象读取并筛选公开字段。
    return ResponseModel(
        message="更新任务成功",
        data=task,
    )


# endregion


__all__ = ["task_router"]
