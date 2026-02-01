from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import db_helper
from app.core.db.rabbitmq import RabbitMQHelper, rabbitmq_helper


DependsSession = Annotated[AsyncSession, Depends(db_helper.session_getter)]
DependsRabbitMQ = Annotated[RabbitMQHelper, Depends(lambda: rabbitmq_helper)]
