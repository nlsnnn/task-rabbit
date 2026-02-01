from fastapi import APIRouter, HTTPException, status

from app.core.schemas.task import TaskCreate, TaskCreateResponse, TaskResponse
from app.core.dependencies.db import DependsSession

from app.api.tasks.service import TaskService


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: DependsSession,
) -> TaskCreateResponse:
    task_id = await TaskService.create_task(session, task_data.payload)
    return TaskCreateResponse(task_id=task_id)


@router.get("/{task_id}")
async def get_task(
    task_id: int,
    session: DependsSession,
) -> TaskResponse:
    task = await TaskService.get_task(session, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return TaskResponse.model_validate(task)
