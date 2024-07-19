from asyncio import TimeoutError, wait_for
from typing import Any, Awaitable, TypeVar

from tenacity import retry, stop_after_attempt, wait_exponential, RetryError, wait_fixed

T = TypeVar('T')

async def with_retry(coro: Awaitable[T], retry_count: int = 3, wait_time: int = 3) -> T:
    @retry(stop=stop_after_attempt(retry_count), wait=wait_fixed(wait_time))
    async def _with_retry() -> T:
        try:
            return await coro
        except Exception as e:
            raise

    try:
        return await _with_retry()
    except RetryError as e:
        raise RetryError(f"Operation failed after {retry_count} attempts: {e}")

async def with_timeout(coro: Awaitable[T], timeout: float) -> T:
    try:
        return await wait_for(coro, timeout=timeout)
    except TimeoutError as e:
        raise TimeoutError(f"Operation timed out: {e}")

async def with_retry_and_timeout(coro: Awaitable[T], timeout: float, retry_count: int = 3, wait_time: int = 3) -> T:
    async def coro_with_timeout() -> T:
        return await with_timeout(coro, timeout)
    
    return await with_retry(coro_with_timeout(), retry_count, wait_time)
