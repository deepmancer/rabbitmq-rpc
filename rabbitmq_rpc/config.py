from typing import Optional, Any, Type, TypeVar
from pydantic import BaseModel, Field
from decouple import config

T = TypeVar('T')

def env_var(field_name: str, default: T, cast_type: Type[T] = str) -> T:
    return config(field_name, default=default, cast=cast_type)

class RabbitMQConfig(BaseModel):
    host: str = Field(default_factory=lambda: env_var("RABBITMQ_HOST", "localhost", str))
    port: int = Field(default_factory=lambda: env_var("RABBITMQ_PORT", 5672, int))
    user: str = Field(default_factory=lambda: env_var("RABBITMQ_USER", "rabbitmq_user", str))
    password: str = Field(default_factory=lambda: env_var("RABBITMQ_PASSWORD", "rabbitmq_password", str))
    vhost: Optional[str] = Field(default_factory=lambda: env_var("RABBITMQ_VHOST", "/", str))
    url: Optional[str] = None

    def get_url(self) -> str:
        if self.url is not None and self.url != "":
            return self.url
        if not self.vhost or self.vhost == "/":
            return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}"
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/{self.vhost}"
