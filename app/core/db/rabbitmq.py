import json
import aio_pika

from contextlib import asynccontextmanager
from typing import AsyncIterator

from aio_pika import Connection, Channel, Exchange, Queue
from aio_pika.pool import Pool

from app.core.config import settings


class RabbitMQHelper:
    def __init__(self, url: str) -> None:
        self.url = url
        self._connection_pool: Pool[Connection] | None = None
        self._channel_pool: Pool[Channel] | None = None

    async def init_pools(self) -> None:
        """Инициализирует connection и channel пулы."""

        async def get_connection() -> Connection:
            return await aio_pika.connect_robust(self.url)

        async def get_channel() -> Channel:
            async with self._connection_pool.acquire() as connection:
                return await connection.channel()

        self._connection_pool = Pool(get_connection, max_size=10)
        self._channel_pool = Pool(get_channel, max_size=20)

    async def close_pools(self) -> None:
        """Закрыть connection и channel пулы."""
        if self._channel_pool:
            await self._channel_pool.close()
        if self._connection_pool:
            await self._connection_pool.close()

    @asynccontextmanager
    async def get_channel(self) -> AsyncIterator[Channel]:
        """Получить канал из пула с контекстным менеджером."""
        if not self._channel_pool:
            raise RuntimeError("RabbitMQ pools not initialized")

        async with self._channel_pool.acquire() as channel:
            yield channel

    async def setup_exchange_and_queue(self) -> tuple[Exchange, Queue]:
        """Инициализирует exchange и очередь."""
        async with self.get_channel() as channel:
            exchange = await channel.declare_exchange(
                settings.rabbitmq.exchange_name,
                aio_pika.ExchangeType.DIRECT,
                durable=True,
            )

            queue = await channel.declare_queue(
                settings.rabbitmq.queue_name,
                durable=True,
            )

            await queue.bind(
                exchange,
                routing_key=settings.rabbitmq.routing_key,
            )

            return exchange, queue

    async def publish_message(self, message: dict):
        """Публикует сообщение в очередь."""
        async with self.get_channel() as channel:
            exchange = await channel.declare_exchange(
                settings.rabbitmq.exchange_name,
                aio_pika.ExchangeType.DIRECT,
                durable=True,
            )

            message_body = json.dumps(message).encode()
            await exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=settings.rabbitmq.routing_key,
            )


rabbitmq_helper = RabbitMQHelper(settings.rabbitmq.url)
