# 🐇📡 RabbitMQ RPC Client

<p align="center">
    <img src="https://img.shields.io/badge/RabbitMQ-FF6600.svg?style=for-the-badge&logo=RabbitMQ&logoColor=white" alt="RabbitMQ">
    <img src="https://img.shields.io/badge/PyPI-3775A9.svg?style=for-the-badge&logo=PyPI&logoColor=white" alt="PyPI">
    <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">
</p>

`rabbitmq_rpc` is a powerful Python package that simplifies the implementation of RPC (Remote Procedure Call) patterns in event-driven microservices. Built on top of the `aio-pika` library, it abstracts the complexities of asynchronous communication with RabbitMQ, providing a seamless and efficient experience for developers.

---

## ✨ Features

- **🚀 Asynchronous RPC Client:** Fully built on `aio-pika`, enabling non-blocking inter-service communication.
- **🌐 Distributed Environment Ready:** Effortlessly connects services across containers and different URLs.
- **📜 Event Registration & Handling:** Easily define, register, and handle events with custom event handlers.
- **🛠️ Customizable RPC Protocol:** Supports any subclass of `aio_pika.patterns.RPC` for tailored RPC interactions.
- **🔒 Thread-Safe Connection:** Utilizes a singleton design pattern to maintain a single instance of the RPC client across threads.
- **⏱️ Retry & Timeout Mechanism:** Built-in support for retrying failed calls and handling timeouts with `with_retry_and_timeout`.
- **🛠️ No Server-side Implementation Required:** Just a running RabbitMQ server—no need for additional RPC server implementations.

## 📦 Installation

Get started by installing `rabbitmq_rpc` using pip:

```sh
pip install git+https://github.com/deepmancer/rabbitmq-rpc.git
```

## 🛠️ Quick Start

### 🎯 Registering Events

In `Service 1`, define event handlers and register them with the `RPCClient` using the `register_event` method:

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
    # Initialize RPC client
    rpc_client = await RPCClient.create(
        host='localhost',
        port=5920,
        user='rabbitmq_user',
        password='rabbitmq_password',
        vhost='/',
        ssl=False,
    )

    # Register event handlers
    await rpc_client.register_event('service1.addition', handler_addition)
    await rpc_client.register_event('service1.subtraction', handle_subtraction)
    await rpc_client.register_event('service1.multiplication', handle_multiplication)
    await rpc_client.register_event('service1.division', handle_division)
    
    # Keep listening for events
    await asyncio.Future()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

### 📞 Calling Events

In `Service 2`, invoke the events defined in `Service 1`:

```python
import asyncio
from rabbitmq_rpc import RPCClient

async def main():
    # Initialize RPC client
    rpc_client = await RPCClient.create(
        host='localhost',
        port=5920,
        user='rabbitmq_user',
        password='rabbitmq_password',
        vhost='/',
        ssl=False,
    )
    
    # Call service1 events
    add_result = await rpc_client.call('service1.addition', data={"x": 1, "y": 2})
    print(f"Addition Result: {add_result}")

    sub_result = await rpc_client.call('service1.subtraction', data={"x": 1, "y": 2})
    print(f"Subtraction Result: {sub_result}")

    mul_result = await rpc_client.call('service1.multiplication', data={"x": 1, "y": 2})
    print(f"Multiplication Result: {mul_result}")

    # Call with timeout and retry mechanism
    div_result = await rpc_client.call('service1.division', data={"x": 5, "y": 2}, timeout=10, retry_count=3)
    print(f"Division Result: {div_result}")

    # Send event without waiting for a response
    rpc_client.send('service1.multiplication', data={"x": 1, "y": 2})    

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

### 🛡️ Error Handling

`rabbitmq_rpc` provides custom exceptions to handle various connection and RPC-related issues:

- `ConnectionError`
- `RPCError`
- `EventRegistrationError`
- `EventPublishError`
- `EventSubscribeError`

### 🔌 Disconnecting

Gracefully disconnect from RabbitMQ when you're done:

```python
await rpc_client.close()
```

## 📄 License

This project is licensed under the Apache License 2.0. For more details, see the [LICENSE](https://github.com/deepmancer/rabbitmq-rpc/blob/main/LICENSE) file.

---

**Elevate your microservices communication with `rabbitmq_rpc` today!** 🐇📡
