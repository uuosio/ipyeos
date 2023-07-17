import asyncio
import time

from multiprocessing import Process, Event, Queue

from ipyeos.transaction import Transaction
from ipyeos import Worker

import requests

def worker(messenger):
    async def run():
        for i in range(5):
            messenger.put(i)
            msg = messenger.get()
            if not msg:
                break
            print(msg)
        messenger.put(None)
        print('exit')
    asyncio.run(run())

def test_messenger():
    in_queue, out_queue = Queue(), Queue()
    messenger = Worker.Messenger(in_queue, out_queue)
    proc = Process(target=worker, args=(Worker.Messenger(out_queue, in_queue),))
    proc.start()
    while True:
        msg = messenger.get()
        if msg is None:
            break
        print(msg)
        messenger.put(f'get {msg} done!')
    proc.join()

def test_query():
    with Transaction(int(time.time())+60*10, '00'*32) as tx:
        tx.add_action('eosio.token', 'sayhello', b'hello, world', {})
        raw_tx = tx.pack().hex()
        r = requests.post('http://127.0.0.1:8809/push_ro_transaction', json={'packed_tx': raw_tx})
        print('+++++r:', r.text)
