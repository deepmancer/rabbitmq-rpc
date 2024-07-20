import json
from typing import Optional, Any, Type, TypeVar
from pydantic import BaseModel, Field, ValidationError, validator
from decouple import config, UndefinedValueError

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
    ssl_connection: Optional[bool] = Field(default_factory=lambda: env_var("RABBITMQ_SSL_CONNECTION", False, cast_type=lambda x: True if x.lower() == "true" else False))
    url: Optional[str] = None

    def get_url(self) -> str:
        if self.url is not None:
            return self.url
        vhost = self.vhost if self.vhost != "/" else ""
        return f"amqp{'s' if self.ssl_connection else ''}://{self.user}:{self.password}@{self.host}:{self.port}/{vhost}"

    def __repr__(self) -> str:
        attributes = self.dict(exclude={"url"})
        attributes['url'] = self.get_url()
        attributes_str = json.dumps(attributes, indent=4)[1:-1]
        return f"{self.__class__.__name__}({attributes_str})"

    def __str__(self) -> str:
        return self.__repr__()
