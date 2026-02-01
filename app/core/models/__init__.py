__all__ = (
    "Base",
    "pk",
    "created_at",
    "updated_at",
    "Task",
)

from app.core.models.base import Base, pk, created_at, updated_at
from app.core.models.task import Task
