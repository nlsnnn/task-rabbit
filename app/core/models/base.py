from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, mapped_column, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import func


pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime,
    mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    ),
]


class Base(DeclarativeBase, AsyncAttrs):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
