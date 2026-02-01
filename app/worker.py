import asyncio
import json
import logging
import random

from aio_pika import IncomingMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db.helper import db_helper
from app.core.db.rabbitmq import rabbitmq_helper

from app.core.models.task import TaskStatus
from app.crud.task import get_task_by_id, update_task_status


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def process_task(task_id: int, session: AsyncSession):
    try:
        task = await get_task_by_id(session, task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return

        logger.info(f"Processing task {task_id}: {task.payload}")
        await update_task_status(session, task_id, TaskStatus.processing)

        processing_time = random.uniform(2, 10)
        await asyncio.sleep(processing_time)

        result = f"Processed '{task.payload}' in {processing_time:.2f}s"
        await update_task_status(session, task_id, TaskStatus.done, result=result)
        logger.info(f"Task {task_id} completed: {result}")

    except Exception as e:
        logger.exception(f"Task {task_id} failed")
        try:
            await update_task_status(
                session, task_id, TaskStatus.failed, result=f"Error: {str(e)}"
            )
        except Exception:
            logger.exception(f"Failed to update task {task_id} status")


async def on_message(message: IncomingMessage):
    async with message.process():
        try:
            body = json.loads(message.body.decode())
            task_id = body.get("task_id")

            if not task_id:
                logger.error(f"Invalid message: {body}")
                return

            async with db_helper.session_maker() as session:
                await process_task(task_id, session)

        except json.JSONDecodeError:
            logger.exception("Failed to decode message")
        except Exception:
            logger.exception("Unexpected error")


async def consume_messages():
    logger.info("Starting worker...")

    await rabbitmq_helper.init_pools()
    await rabbitmq_helper.setup_exchange_and_queue()
    logger.info("Connected to RabbitMQ")

    async with rabbitmq_helper.get_channel() as channel:
        await channel.set_qos(prefetch_count=settings.rabbitmq.prefetch_count)
        queue = await channel.declare_queue(settings.rabbitmq.queue_name, durable=True)

        logger.info(f"Listening on queue: {settings.rabbitmq.queue_name}")

        await queue.consume(on_message, no_ack=False)

        await asyncio.Future()  # Run forever


async def main():
    try:
        await consume_messages()
    finally:
        await rabbitmq_helper.close_pools()
        await db_helper.dispose()
        logger.info("Cleanup complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped")
