import asyncio
import pytest
from ipyeos import rate_limit

def int_to_ip(n):
    return ".".join(str((n >> (i << 3)) & 0xFF) for i in reversed(range(4)))

@pytest.mark.asyncio
async def test_scheduler():
    scheduler = rate_limit.WeightedFairScheduler()

    async def test_task(delay, return_value):
        await asyncio.sleep(delay)
        return return_value
    task1 = scheduler.add_task('127.0.0.1', 'https://127.0.0.1/v1/chain/get_info', test_task(0.1, 'delay 0.1'))
    task2 = scheduler.add_task('127.0.0.2', 'https://127.0.0.1/v1/chain/get_info', test_task(0.2, 'delay 0.2'))
    assert 'delay 0.2' == await scheduler._process_task()
    assert 'delay 0.1' == await scheduler._process_task()
    assert None == await scheduler._process_task()

    assert 'delay 0.1' == await task1.wait()
    assert 'delay 0.2' == await task2.wait()

    task1 = scheduler.add_task('127.0.0.1', 'https://127.0.0.1/v1/chain/get_info', test_task(0.1, 'delay 0.1'))
    task2 = scheduler.add_task('127.0.0.2', 'https://127.0.0.1/v1/chain/get_info', test_task(0.2, 'delay 0.2'))
    assert 'delay 0.1' == await scheduler._process_task()
    assert 'delay 0.2' == await scheduler._process_task()
    assert 'delay 0.1' == await task1.wait()
    assert 'delay 0.2' == await task2.wait()

    async def test_task(delay, return_value):
        raise Exception('test exception')
    task1 = scheduler.add_task('127.0.0.1', 'https://127.0.0.1/v1/chain/get_info', test_task(0.1, 'delay 0.1'))
    ret = await scheduler._process_task()
    assert isinstance(ret, Exception)
    assert str(ret) == 'test exception'

    ret = await task1.wait()
    assert isinstance(ret, Exception)
    assert str(ret) == 'test exception'

    async def test_task(delay, return_value):
        return return_value

    scheduler = rate_limit.WeightedFairScheduler(window_time=3)
    for i in range(rate_limit.MAX_CONNECTIONS):
        scheduler.add_task(int_to_ip(i), f'https://{i}', test_task(0.1, f'{i}'))

    assert len(scheduler.connections) == rate_limit.MAX_CONNECTIONS

    i = rate_limit.MAX_CONNECTIONS
    assert None == scheduler.add_task(int_to_ip(rate_limit.MAX_CONNECTIONS), f'https://{i}', test_task(0.1, f'{i}'))

    await asyncio.sleep(3.0)
    assert None == await scheduler._process_task()
    assert len(scheduler.connections) == 0

    task = scheduler.add_task(int_to_ip(rate_limit.MAX_CONNECTIONS), f'https://100', test_task(0.1, f'100'))
    assert '100' == await scheduler._process_task()
    assert '100' == await task.wait()

