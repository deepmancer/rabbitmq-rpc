import json
from typing import Optional, Any, Type, TypeVar, Callable
from pydantic import BaseModel, Field, ValidationError, validator
from decouple import config
from aio_pika.connection import make_url, URL

T = TypeVar('T')

def env_var(field_name: str, default = None, cast_type = str) -> T:
    try:
        value = config(field_name, default=default)
        return cast_type(value)
    except Exception:
        return default

class RabbitMQConfig(BaseModel):
    host: Optional[str] = Field(default_factory=lambda: env_var("RABBITMQ_HOST", "localhost", str))
    port: Optional[int] = Field(default_factory=lambda: env_var("RABBITMQ_PORT", 5672, int))
    user: Optional[str] = Field(default_factory=lambda: env_var("RABBITMQ_USER", "rabbitmq_user", str))
    password: Optional[str] = Field(default_factory=lambda: env_var("RABBITMQ_PASS", "rabbitmq_password", str))
    vhost: Optional[str] = Field(default_factory=lambda: env_var("RABBITMQ_VHOST", "/", str))
    ssl_connection: Optional[bool] = Field(default_factory=lambda: env_var("RABBITMQ_SSL_CONNECTION", False, cast_type=lambda s: s.lower() in ['true', '1']))
    url: Optional[str] = Field(default=None)

    def __repr__(self) -> str:
        attributes = self.dict(exclude={"url"})
        attributes['url'] = self.get_url()
        attributes_str = json.dumps(attributes, indent=4)[1:-1]
        return f"{self.__class__.__name__}({attributes_str})"

    def __str__(self) -> str:
        return self.__repr__()

    def get_url(self) -> URL:
        return make_url(
            url=self.url,
            host=self.host,
            port=self.port,
            login=self.user,
            password=self.password,
            virtualhost=self.vhost,
            ssl=self.ssl_connection
        )
