"""任务 API 路由。"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user import User
from app.schemas.base import ResponseModel
from app.schemas.task_request import TaskCreateRequest
from app.schemas.task_response import TaskCreateResponse
from app.services.task import create_task_service

# 任务领域接口统一使用 /tasks 路径前缀和中文 Swagger 标签。
task_router = APIRouter(tags=["任务"], prefix="/tasks")


# region 任务创建
@task_router.post(
    "create",
    response_model=ResponseModel[TaskCreateResponse]
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
        code=200,
        message="创建任务成功",
        data=new_task,
    )


# endregion


__all__ = ["task_router"]
