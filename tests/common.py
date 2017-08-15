import asyncio
import unittest

def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


def get_mock_coro(return_value):
    @asyncio.coroutine
    def mock_coro(*args, **kwargs):
        return return_value
    return unittest.mock.Mock(wraps=mock_coro)


def get_mock_coro_pop_list(return_values):
    @asyncio.coroutine
    def mock_coro(*args, **kwargs):
        return return_values.pop(0)
    return unittest.mock.Mock(wraps=mock_coro)
