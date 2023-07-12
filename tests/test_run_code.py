import requests

def test1():
    code = '''
    #from ipyeos import eos
    import sys
    import exec_result
    def test():
        eos.set_info_level("net_plugin_impl")
        eos.set_info_level("default")
    #eos.post(test)
    a = 'hello'
    exec_result.set({"a": a})
    '''

    r = requests.post('http://127.0.0.1:7777/exec', json={'code': code})
    print(r.text)

def test2():
    code = '''
import asyncio
from ipyeos import exec_result
async def shutdown():
    loop = asyncio.get_running_loop()
    tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
    # tasks = [t for t in asyncio.all_tasks(loop)]
    for task in tasks:
        logger.info('cancle task: %s', task)
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()
asyncio.create_task(shutdown())
exec_result.set('Done!')
    '''
    r = requests.post('http://127.0.0.1:7777/exec', json={'code': code})
    print(r.text)

test2()
