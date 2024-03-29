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
from ipyeos import eos
from ipyeos import node, net
network = node.get_network()

peer = 'bp.cryptolions.io:9876'
network.peers.append(peer)

conn = net.OutConnection(network.chain, peer)
conn.add_goway_listener(network.on_goway)
network.connections.append(conn)
exec_result.set("Done!")
'''

    code = '''
from ipyeos import eos
from ipyeos import node, net
network = node.get_network()

peer = 'bp.cryptolions.io:9876'
conns = [c for c in network.connections if not c.peer == 'bp.cryptolions.io:9876']
for c in conns:
    network.connections.remove(c)
exec_result.set("Done!")
'''
    r = requests.post('http://127.0.0.1:7777/exec', json={'code': code})
    print(r.text)

def test3():
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

def test_4():
    code = '''
from ipyeos import exec_result
from ipyeos.chain import Chain
chain = Chain.attach()
head_num = chain.head_block_num()
exec_result.set(f'{head_num} Done!')
    '''
    r = requests.post('http://127.0.0.1:7777/exec', json={'code': code})
    print(r.text)
