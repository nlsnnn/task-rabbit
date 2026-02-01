from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    url: str


class RabbitMQConfig(BaseModel):
    url: str
    queue_name: str = "task_queue"
    exchange_name: str = "task_exchange"
    routing_key: str = "task.new"
    prefetch_count: int = 5


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP__",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    debug: bool = False
    db: DatabaseConfig
    rabbitmq: RabbitMQConfig


settings = Settings()
