# rabbitmq-rpc

`rabbitmq_rpc` is a Python package that provides an easy-to-use RabbitMQ RPC client for event-driven microservices. Built upon the `aio-pika` library, it simplifies interactions with RabbitMQ by handling the complexities of asynchronous communication and connection management.

# Features
- **aio-pika Compatibility:** Fully compatible with the `aio-pika` library.
- **Asynchronous RPC Client:** Built on top of `aio-pika`, it supports asynchronous communication for inter-service communication.
- **Distributed Environment Integration:** Connects services across different containers and URLs.
- **Event Registration and Handling:** Easily register and handle events with custom event handlers.
- **Customizable RPC Protocol:** Supports any subclass of the `aio_pika.patterns.RPC` class.
- **Thread-safe Connection:** Ensures that a single instance of the RPC client is used across threads using a singleton design pattern.
- **Retry and Timeout Mechanism:** Built-in support for retrying failed calls and handling timeouts using `with_retry_and_timeout`.
- **No Server-side Implementation Required:**  Only requires a running RabbitMQ server, with no need for RPC server implementations.

## Installation

To install `rabbitmq_rpc`, use pip:

```sh
pip install git+https://github.com/alirezaheidari-cs/rabbitmq-rpc.git
```

# Usage
Here's a basic example of how to use the RPCClient class in your project:

## Registering Events:
First, `Service 1` defines its event handlers and registers them with the RPCClient, simply by calling the `register_event` method:

```python
import asyncio
from rabbitmq_rpc import RPCClient

async def handler_addition(x, y):
    return x + y

async def handle_subtraction(x, y):
    return x - y

async def handle_multiplication(x, y):
    return x * y

async def handle_division(x, y):
    return x / y

async def main():
    # Starting RPC client
    rpc_client = await RPCClient.create(
        host='localhost',
        port=5920,
        user='rabbitmq_user',
        password='rabbitmq_password',
        vhost='/',
        ssl=False,
    )

    # Registering events
    await rpc_client.register_event('service1.addition', handler_addition)
    await rpc_client.register_event('service1.subtraction', handle_subtraction)
    await rpc_client.register_event('service1.multiplication', handle_multiplication)
    await rpc_client.register_event('service1.division', handle_division)
    
    # Start listening to events forever
    await asyncio.Future()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

```

## Calling Events
Next, `Service 2` calls the events defined in `Service 1` (micro)service:

```python
import asyncio
from rabbitmq_rpc import RPCClient

async def main():
    # Starting RPC client
    rpc_client = await RPCClient.create(
        host='localhost',
        port=5920,
        user='rabbitmq_user',
        password='rabbitmq_password',
        vhost='/',
        ssl=False,
    )
    
    # Calling service1 events
    add_result = await rpc_client.call('service1.addition', data={"x": 1, "y": 2})
    print(add_result)
    sub_result = await rpc_client.call('service1.subtraction', data={"x": 1, "y": 2})
    print(sub_result)
    mul_result = await rpc_client.call('service1.multiplication', data={"x": 1, "y": 2})
    print(mul_result)

    # Specifying timeout and retry count per call
    div_result = await rpc_client.call('service1.division', data={"x": 5, "y": 2}, timeout=10, retry_count=3)
    print(div_result)

    # Sending an event without waiting for the response    
    rpc_client.send('service1.multiplication', data={"x": 1, "y": 2})    

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

```

## Error Handling
The package provides custom exceptions to handle various connection and RPC-related errors:

- `ConnectionError`
- `RPCError`
- `EventRegistrationError`
- `EventPublishError`
- `EventSubscribeError`

## Disconnecting
To gracefully disconnect from RabbitMQ:

```python
await rpc_client.close()
```

# License
This project is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/alirezaheidari-cs/rabbitmq-rpc/blob/main/LICENSE) file for more details.
