from .native_modules import _read_write_lock

class ReadWriteLock(object):
    def __init__(self, name):
        self._lock = _read_write_lock.new(name)
    
    def free(self):
        _read_write_lock.free_read_write_lock(self._lock)
    
    def __del__(self):
        if not self._lock:
            return
        self.free()
        self._lock = None
    
    def acquire_read_lock(self):
        _read_write_lock.acquire_read_lock(self._lock)
    
    def release_read_lock(self):
        _read_write_lock.release_read_lock(self._lock)

    def acquire_write_lock(self):
        _read_write_lock.acquire_write_lock(self._lock)
    
    def release_write_lock(self):
        _read_write_lock.release_write_lock(self._lock)
