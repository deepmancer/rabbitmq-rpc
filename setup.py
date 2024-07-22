from setuptools import setup, find_packages

setup(
    name="rabbitmq_rpc",
    version="0.4.0",
    description="A RabbitMQ RPC client package for easy event-driven microservices",
    author="Alireza Heidari",
    author_email="alirezaheidari.cs@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "aio-pika",
        "tenacity",
        "pydantic",
        "python-decouple",
    ],
    license='Apache License 2.0',
    keywords="event rpc aio-pika rabbitmq microservice",
    url="https://github.com/alirezaheidari-cs/rabbitmq_rpc",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
