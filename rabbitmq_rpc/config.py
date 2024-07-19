from typing import Optional
from pydantic import BaseModel, Field

class RabbitMQConfig(BaseModel):
    host: str = Field(...)
    port: int = Field(...)
    user: str = Field(...)
    password: str = Field(...)
    vhost: Optional[str] = Field(None)

    @property
    def url(self) -> str:
        if self.vhost is None or self.vhost == "" or self.vhost == "/":
            return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}"
    
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/{self.vhost}"
