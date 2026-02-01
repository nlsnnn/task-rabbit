from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task import create_task, get_task_by_id
from app.core.models.task import Task
from app.core.db.rabbitmq import RabbitMQHelper


class TaskService:
    @staticmethod
    async def create_task(
        session: AsyncSession,
        payload: str,
        rabbitmq: RabbitMQHelper,
    ) -> int:
        """
        Создает задачу в БД и отправляет её в RabbitMQ очередь.
        Возвращает ID созданной задачи.
        """
        task = await create_task(session, payload)
        await rabbitmq.publish_message({"task_id": task.id})
        return task.id

    @staticmethod
    async def get_task(session: AsyncSession, task_id: int) -> Task | None:
        """Получает задачу по ID."""
        return await get_task_by_id(session, task_id)
