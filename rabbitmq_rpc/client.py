import json
import logging
import threading
import asyncio
from asyncio import AbstractEventLoop, TimeoutError
from typing import Type, Union, Callable, Any, Optional, Dict

import aio_pika
from aio_pika import DeliveryMode, Channel, ExchangeType, Message, exceptions
from aio_pika.connection import URL
from aio_pika.patterns import RPC, JsonRPC
from pydantic import BaseModel

from .config import RabbitMQConfig
from .exceptions import ConnectionError, RPCError, EventRegistrationError, EventPublishError, EventSubscribeError
from .utils import with_retry_and_timeout

logging.basicConfig(level=logging.INFO)

class RPCClient:
    _instances: Dict[str, 'RPCClient'] = {}
    _locks: Dict[str, threading.Lock] = {}

    def __init__(
        self,
        config: RabbitMQConfig,
        rpc_cls: Type[Union[RPC, JsonRPC]] = RPC,
        loop: Optional[AbstractEventLoop] = None,
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        self.config: RabbitMQConfig = config
        self.rpc_cls: Type[Union[RPC, JsonRPC]] = rpc_cls
        self.loop: Optional[AbstractEventLoop] = loop
        self.logger: logging.Logger = logger

        self.rpc: Optional[Union[RPC, JsonRPC]] = None
        self.connection: Optional[aio_pika.robust_connection.RobustConnection] = None

    @property
    def url(self) -> URL:
        return self.config.get_url()

    @staticmethod
    async def create(
        config: Optional[RabbitMQConfig] = None,
        rpc_cls: Type[Union[RPC, JsonRPC]] = RPC,
        loop: Optional[AbstractEventLoop] = None,
        logger: Optional[logging.Logger] = None,
        url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        vhost: Optional[str] = None,
        ssl: bool = False,
        **kwargs, 
    ) -> 'RPCClient':
        if config is None:
            config = RabbitMQConfig(
                host=host,
                port=port,
                user=user,
                password=password,
                vhost=vhost,
                url=url,
                ssl_connection=ssl,
            )

        url = config.get_url()

        if url not in RPCClient._locks:
            RPCClient._locks[url] = threading.Lock()

        with RPCClient._locks[url]:
            if url not in RPCClient._instances:
                if loop is None:
                    loop = asyncio.get_event_loop()
                RPCClient._instances[url] = await RPCClient.__create_instance(
                    config=config,
                    logger=logger,
                    loop=loop,
                    rpc_cls=rpc_cls,
                    **kwargs,
                )

        return RPCClient._instances[url]

    @staticmethod
    async def __create_instance(
        config: RabbitMQConfig,
        rpc_cls: Type[Union[RPC, JsonRPC]],
        loop: AbstractEventLoop,
        logger: logging.Logger,
        **kwargs,
    ) -> 'RPCClient':
        instance = RPCClient(config=config, rpc_cls=rpc_cls, loop=loop, logger=logger)
        await instance.connect(**kwargs)
        return instance

    @property
    def is_connected(self) -> bool:
        return self.rpc is not None and not self.rpc.channel.is_closed

    async def connect(self, **kwargs: Any) -> None:
        try:
            self.connection = await aio_pika.connect_robust(
                url=self.url, loop=self.loop,
            )
            channel = await self.connection.channel()
            self.rpc = await self.rpc_cls.create(channel, **kwargs)
            self.logger.info("Connected to RabbitMQ")
        except (exceptions.AMQPConnectionError, exceptions.AMQPChannelError) as e:
            self.logger.error(f"Failed to connect to RabbitMQ at {self.url}: {str(e)}")
            raise ConnectionError(f"Failed to connect to RabbitMQ: {str(e)}")

    async def reconnect(self, **kwargs: Any) -> None:
        try:
            await self.close()
            await self.connect(**kwargs)
            self.logger.info("Reconnected to RabbitMQ")
        except ConnectionError as e:
            self.logger.error(f"Failed to reconnect to RabbitMQ: {str(e)}")
            raise e

    async def close(self) -> None:
        if self.connection:
            try:
                await self.connection.close()
                self.rpc = None
                self.connection = None
                self.logger.info("Closed RabbitMQ connection")
            except exceptions.AMQPError as e:
                self.logger.error(f"Failed to close RabbitMQ connection: {str(e)}")
                raise ConnectionError(f"Failed to close RabbitMQ connection: {str(e)}")

    def set_event_loop(self, loop: AbstractEventLoop) -> None:
        self.loop = loop
        if self.rpc:
            self.rpc.loop = loop

    def set_logger(self, logger: logging.Logger) -> None:
        self.logger = logger

    def set_rpc_class(self, rpc_cls: Type[Union[RPC, JsonRPC]]) -> None:
        self.rpc_cls = rpc_cls

    def get_logger(self) -> logging.Logger:
        return self.logger

    def get_rpc_class(self) -> Type[Union[RPC, JsonRPC]]:
        return self.rpc_cls

    def get_connection(self) -> Optional[aio_pika.robust_connection.RobustConnection]:
        return self.connection

    async def get_channel(self) -> Channel:
        if not self.is_connected:
            await self.connect()
        return self.rpc.channel

    async def send(
        self,
        event: str,
        data: Union[dict, Type[BaseModel]],
        expiration: Optional[int] = None,
        priority: int = 5,
        delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT,
        timeout: Optional[float] = None,
        retry_count: int = 3,
        **kwargs: Any,
    ) -> None:
        if not self.is_connected:
            raise ConnectionError("RPCClient is not connected")
        try:
            if not isinstance(data, dict):
                data = data.dict()
            await with_retry_and_timeout(
                self.rpc.call(
                    method_name=event,
                    kwargs=data,
                    expiration=expiration,
                    priority=priority,
                    delivery_mode=delivery_mode,
                    **kwargs,
                ),
                timeout,
                retry_count,
            )
        except (TimeoutError, exceptions.AMQPError) as e:
            self.logger.error(f"Failed to send event {event}: {str(e)}")
            raise RPCError(f"Failed to send event {event}: {str(e)}")

    async def call(
        self,
        event: str,
        data: Union[dict, Type[BaseModel]],
        expiration: Optional[int] = None,
        priority: int = 5,
        delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT,
        timeout: Optional[float] = None,
        retry_count: int = 3,
        **kwargs: Any,
    ) -> Any:
        if not self.is_connected:
            raise ConnectionError("RPCClient is not connected")
        try:
            if not isinstance(data, dict):
                data = data.dict()
            return await with_retry_and_timeout(
                self.rpc.call(
                    method_name=event,
                    kwargs=data,
                    expiration=expiration,
                    priority=priority,
                    delivery_mode=delivery_mode,
                    **kwargs,
                ),
                timeout,
                retry_count,
            )
        except (TimeoutError, exceptions.AMQPError) as e:
            self.logger.error(f"Failed to call event {event}: {str(e)}")
            raise RPCError(f"Failed to call event {event}: {str(e)}")

    async def register_event(self, event: str, handler: Callable[..., Any], **kwargs: Any) -> None:
        if not self.is_connected:
            raise ConnectionError("RPCClient is not connected")
        try:
            await self.rpc.register(event, handler, **kwargs)
            self.logger.info(f"Registered event handler for {event}")
        except (exceptions.AMQPError, ValueError) as e:
            self.logger.error(f"Failed to register event handler for {event}: {str(e)}")
            raise EventRegistrationError(f"Failed to register event handler for {event}: {str(e)}")

    async def unregister_event(self, handler: Callable[..., Any]) -> None:
        if not self.is_connected:
            raise ConnectionError("RPCClient is not connected")
        try:
            await self.rpc.unregister(handler)
            self.logger.info("Unregistered event handler")
        except (exceptions.AMQPError, ValueError) as e:
            self.logger.error(f"Failed to unregister event handler: {str(e)}")
            raise EventRegistrationError(f"Failed to unregister event handler: {str(e)}")

    async def publish_event(
        self, 
        exchange_name: str, 
        routing_key: str, 
        message: Union[dict, Type[BaseModel]], 
        exchange_type: ExchangeType = ExchangeType.DIRECT, 
        durable: bool = True, 
        timeout: Optional[float] = None,
        retry_count: int = 3,
        **kwargs: Any,
    ) -> None:
        if not self.is_connected:
            raise ConnectionError("RPCClient is not connected")
        try:
            if not isinstance(message, dict):
                message = message.dict()
            await with_retry_and_timeout(
                self._publish(exchange_name, routing_key, message, exchange_type, durable, **kwargs),
                timeout,
                retry_count,
            )
        except (TimeoutError, exceptions.AMQPError) as e:
            self.logger.error(f"Failed to publish event to exchange {exchange_name}: {str(e)}")
            raise EventPublishError(f"Failed to publish event to exchange {exchange_name}: {str(e)}")

    async def subscribe_event(
        self, 
        queue_name: str, 
        handler: Callable[..., Any], 
        durable: bool = True, 
        timeout: Optional[float] = None, 
        retry_count: int = 3, 
        **kwargs: Any,
    ) -> None:
        if not self.is_connected:
            raise ConnectionError("RPCClient is not connected")
        try:
            await with_retry_and_timeout(
                self._subscribe(queue_name, handler, durable, **kwargs),
                timeout,
                retry_count,
            )
        except (TimeoutError, exceptions.AMQPError) as e:
            self.logger.error(f"Failed to subscribe to queue {queue_name}: {str(e)}")
            raise EventSubscribeError(f"Failed to subscribe to queue {queue_name}: {str(e)}")

    async def _subscribe(
        self, 
        queue_name: str, 
        handler: Callable[..., Any], 
        durable: bool, 
        **kwargs: Any,
    ) -> None:
        try:
            channel = await self.connection.channel()
            queue = await channel.declare_queue(queue_name, durable=durable, **kwargs)
            await queue.consume(handler)
            self.logger.info(f"Subscribed to queue {queue_name}")
        except (exceptions.AMQPError, ValueError) as e:
            self.logger.error(f"Failed to subscribe to queue {queue_name}: {str(e)}")
            raise EventSubscribeError(f"Failed to subscribe to queue {queue_name}: {str(e)}")

    async def _publish(
        self, 
        exchange_name: str, 
        routing_key: str, 
        message: dict, 
        exchange_type: ExchangeType, 
        durable: bool, 
        **kwargs: Any,
    ) -> None:
        try:
            channel = await self.connection.channel()
            exchange = await channel.declare_exchange(
                exchange_name, 
                exchange_type=exchange_type,
                durable=durable,
            )
            await exchange.publish(
                Message(
                    body=json.dumps(message).encode(),
                    content_type='application/json',
                    delivery_mode=DeliveryMode.PERSISTENT,
                ),
                routing_key=routing_key,
                **kwargs,
            )
            self.logger.info(f"Published event to exchange {exchange_name} with routing key {routing_key}")
        except (exceptions.AMQPError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to publish event: {str(e)}")
            raise EventPublishError(f"Failed to publish event: {str(e)}")

    def __repr__(self) -> str:
        return f"RPCClient(config={self.config}, rpc_cls={self.rpc_cls})"
