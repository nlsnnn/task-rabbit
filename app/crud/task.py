from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.task import Task, TaskStatus


async def create_task(session: AsyncSession, payload: str) -> Task:
    task = Task(payload=payload, status=TaskStatus.pending)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_task_by_id(session: AsyncSession, task_id: int) -> Task | None:
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_task_status(
    session: AsyncSession, task_id: int, status: TaskStatus, result: str | None = None
) -> Task | None:
    task = await get_task_by_id(session, task_id)
    if task:
        task.status = status
        if result is not None:
            task.result = result
        await session.commit()
        await session.refresh(task)
    return task

