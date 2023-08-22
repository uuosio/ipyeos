import time
import multiprocessing as mp
from ipyeos.bases.read_write_lock import ReadWriteLock


def read_lock_worker(proc_id):
    lock = ReadWriteLock("testlock")
    print(f"Process {proc_id} started")
    for i in range(3):
        lock.acquire_read_lock()
        print(f"Process {proc_id} acquired read lock {i}")
        time.sleep(0.01)
        lock.release_read_lock()
        print(f"Process {proc_id} released read lock {i}")

def test_rw_lock():
    print()
    lock = ReadWriteLock("testlock")
    lock.acquire_read_lock()
    lock.release_read_lock()

    lock.acquire_write_lock()
    lock.release_write_lock()

    p1 = mp.Process(target=read_lock_worker, args=(1,))
    p1.start()

    p2 = mp.Process(target=read_lock_worker, args=(2,))
    p2.start()

    for i in range(3):
        lock.acquire_write_lock()
        print(f"Main process acquired write lock {i}")
        time.sleep(2)
        lock.release_write_lock()
        print(f"Main process released write lock {i}")
        time.sleep(0.001)

    p1.join()
    p2.join()
