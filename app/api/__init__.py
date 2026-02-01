from fastapi import FastAPI, APIRouter

from app.api.tasks.router import router as task_router


def register_routers(app: FastAPI):
    """Регистрирует маршруты API в приложении FastAPI."""
    root_router = APIRouter(tags=["Root"])

    @root_router.get("/ping")
    async def ping():
        return {"message": "PONG"}

    app.include_router(root_router)
    app.include_router(task_router)
