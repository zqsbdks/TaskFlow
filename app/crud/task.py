
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task
from app.models.user import User


async def create_task(task_data,current_user: User,db:AsyncSession):
    select(Task).where(Task.user_id == current_user.id)
    task = Task(**task_data)
    task.user_id = current_user.id
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task