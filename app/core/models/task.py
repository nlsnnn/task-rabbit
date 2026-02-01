from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import Base, pk, created_at, updated_at
from enum import Enum as PyEnum


class TaskStatus(str, PyEnum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"


class Task(Base):
    id: Mapped[pk]
    payload: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.pending
    )
    result: Mapped[str | None] = mapped_column(nullable=True)

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
