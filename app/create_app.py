from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api import register_routers
from app.core.db import db_helper
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db_helper.dispose()


def create_fastapi_app():
    app = FastAPI(
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    register_routers(app)

    return app
