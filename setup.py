from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rabbitmq_rpc",
    version="1.0.0",
    description="A RabbitMQ RPC client package for easy event-driven microservices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alireza Heidari",
    author_email="alirezaheidari.cs@gmail.com",
    url="https://github.com/alirezaheidari-cs/rabbitmq-rpc",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "aio-pika",
        "tenacity",
        "pydantic>=2",
        "python-decouple",
    ],
    license='Apache License 2.0',
    keywords="event rpc aio-pika rabbitmq microservice remote-procedure-call async python",
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
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.6",
    project_urls={
        "Documentation": "https://github.com/alirezaheidari-cs/rabbitmq-rpc#readme",
        "Source": "https://github.com/alirezaheidari-cs/rabbitmq-rpc",
        "Tracker": "https://github.com/alirezaheidari-cs/rabbitmq-rpc/issues",
    },
)
