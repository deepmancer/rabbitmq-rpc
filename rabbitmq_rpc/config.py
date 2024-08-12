import json
from typing import Optional, TypeVar

from aio_pika.connection import make_url
from decouple import config
from pydantic import BaseModel, Field

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
    ssl: Optional[bool] = Field(default=False)
    url: Optional[str] = Field(default=None)

    def __repr__(self) -> str:
        attributes = self.dict(exclude={"url"})
        attributes['url'] = self.get_url()
        attributes_str = json.dumps(attributes, indent=4)[1:-1]
        return f"{self.__class__.__name__}({attributes_str})"

    def __str__(self) -> str:
        return self.__repr__()

    def get_url(self) -> str:
        return str(
            make_url(
                url=self.url,
                host=self.host,
                port=self.port,
                login=self.user,
                password=self.password,
                virtualhost=self.vhost,
                ssl=self.ssl
            )
        )
