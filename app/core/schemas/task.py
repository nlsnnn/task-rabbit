from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.core.models.task import TaskStatus


class TaskCreate(BaseModel):
    payload: str


class TaskCreateResponse(BaseModel):
    task_id: int


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payload: str
    status: TaskStatus
    result: str | None
    created_at: datetime
    updated_at: datetime
