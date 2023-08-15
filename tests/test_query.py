import asyncio
import httpx
import pytest
import requests
import time

from multiprocessing import Process, Queue, Condition, Value, Lock, shared_memory

from ipyeos.signed_transaction import SignedTransaction
from ipyeos import Worker


def worker(messenger):
    async def run():
        start = time.monotonic()
        count = 10000
        for i in range(count):
            messenger.put(i)
            msg = messenger.get()
            if not msg:
                break
            # print(msg)
        duration = time.monotonic() - start
        print('+++++QPS:', count/duration)
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
        # print(msg)
        messenger.put(f'get {msg} done!')
    proc.join()

async def run_query(port):
    client = httpx.AsyncClient()
    with SignedTransaction(int(time.time())+60*10, '00'*32) as tx:
        tx.add_action('eosio.stake', 'sayhello', b'hello, world', {})
        raw_tx = tx.pack().hex()
        start = time.monotonic()
        count = 100
        for i in range(count):
            r = await client.post(f'http://127.0.0.1:{port}/push_ro_transaction', json={'packed_tx': raw_tx})
            # print('+++++r:', r.text)
        end = time.monotonic()
        print('+++++QPS:', count/(end-start))
    await client.aclose()

def run_in_subprocess(port):
    asyncio.run(run_query(port))

def test_query_performance():
    processes = [Process(target=run_in_subprocess, args=(port,)) for port in (8809, 8810, 8811, 8812)]
    for p in processes:
        p.start()
    
    for p in processes:
        p.join()

@pytest.mark.asyncio
async def test_ro_tx():
    port = 8809
    client = httpx.AsyncClient()
    with SignedTransaction(int(time.time())+60*10, '00'*32) as tx:
        tx.add_action('eosio.stake', 'sayhello', b'hello, world', {})
        raw_tx = tx.pack().hex()
        r = await client.post(f'http://127.0.0.1:{port}/push_ro_transaction', json={'packed_tx': raw_tx})
        print(r.text)
    await client.aclose()


class ReadWriteLock:
    class _RLock:
        def __init__(self, lock):
            self._lock = lock

        def __enter__(self):
            self._lock._read_ready.acquire()
            self._lock._readers.value += 1
            self._lock._read_ready.release()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._lock._read_ready.acquire()
            self._lock._readers.value -= 1
            if not self._lock._readers.value:
                self._lock._read_ready.notify_all()
            self._lock._read_ready.release()

    class _WLock:
        def __init__(self, lock, i):
            self._lock = lock
            self.i = i

        def __enter__(self):
            self._lock._read_ready.acquire()
            while self._lock._readers.value > 0:
                self._lock._read_ready.wait()
            print('\n++++++++++++++++++++++++++WLock', self.i)

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._lock._read_ready.notify_all()
            print('++++++++++++++++++++++++++WUnlock', self.i, '\n')
            self._lock._read_ready.release()

    def __init__(self):
        self._read_ready = Condition(Lock())
        self._readers = Value('i', 0)  # integer, initially 0

    def rlock(self):
        return self._RLock(self)

    def wlock(self, i):
        return self._WLock(self, i)

def reader_process(i, rwlock, resource):
    for j in range(10):
        with rwlock.rlock():
            print(f"{j}: Reader {i} reads {resource.buf[0]}")
        time.sleep(0.1)

def writer_process(i, rwlock, resource):
    for j in range(5):
        with rwlock.wlock(i):
            resource.buf[0] = i
            print(f"{j}: Writer {i} writes {i}")
        time.sleep(0.2)

def test_rw_lock():
    resource = shared_memory.SharedMemory(create=True, size=1)
    rwlock = ReadWriteLock()

    # Create and start 3 reader processes and 2 writer processes
    processes = [Process(target=reader_process, args=(i, rwlock, resource))
                for i in range(3)]
    processes += [Process(target=writer_process, args=(i, rwlock, resource))
                for i in range(3, 5)]

    for process in processes:
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()
