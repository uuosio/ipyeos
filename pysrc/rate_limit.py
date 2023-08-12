import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer
from queue import PriorityQueue

from . import eos, log
from .multi_index import key_u64_value_double_index, secondary_double_index

cache = Cache(Cache.MEMORY, serializer=PickleSerializer())

REQUESTS_PER_MINUTE = 100
BLOCK_INTERVAL = 60 # Block for 1 minute if the limit is exceeded

logger = log.get_logger(__name__)

class Connection:
    def __init__(self, name, priority):
        self.name = name
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __repr__(self):
        return f"Task(name={self.name}, priority={self.priority})"

class Task(object):
    def __init__(self, task):
        self.task = task
        self.event = asyncio.Event()
        self.ret = None

    async def run(self):
        self.ret = await self.task
        self.event.set()

    async def wait(self):
        await self.event.wait()
        return self.ret

class Connection:
    def __init__(self, id, host, weight=1):
        self.id = id
        self.host = host
        self.tasks = []
        self.weight = weight
        self.served_time = 0
        self.served_times = key_u64_value_double_index()

    def __lt__(self, other):
        return self.relative_priority() < other.relative_priority()

    await def process(self):
        if not self.tasks:
            return None

        task = self.tasks.pop(0)
        start = time.monotonic()
        await task.run()
        duration = time.monotonic() - start
        self.served_time += duration
        current_time = int(time.time)
        ret = self.served_times.last()
        if ret:
            last_duration, last_time = ret
            if last_time == current_time:
                last_duration += duration
                self.served_times.modify(last_time, last_duration)
            else:
                self.served_times.create(current_time, duration)
        else:
            self.served_times.create(current_time, duration)

    def add_task(self, task):
        self.tasks.append(Task(task))
    
    def clear_expired(self, window_time):
        current_time = int(time.time)
        while True:
            ret = self.served_times.first()
            if not ret:
                break
            duration, time_slot = ret
            if current_time - time_slot < window_time:
                break
            self.served_time -= duration
            self.served_times.remove(time_slot)

    def is_done(self):
        return len(self.tasks) == 0

    def relative_priority(self):
        if not self.tasks:
            return 0.0
        if self.served_time > 0:
            return self.weight / self.served_time
        else:
            return float('inf')

class WeightedFairScheduler:
    def __init__(self):
        self.connections = {}
        self.id_host_map = {}
        self.host_id_map = {}
        self.connection_counter = 0
        self.priority_index = secondary_double_index()
        self.window_time = 60*10

    def add_task(self, host, task):
        if not host in self.connections:
            self.connection_counter += 1
            conn = Connection(self.connection_counter, host)
            self.connections[self.connection_counter] = conn
            self.id_host_map[self.connection_counter] = host
            self.host_id_map[host] = self.connection_counter
            self.priority_index.create(self.connection_counter, conn.relative_priority())
        id = self.host_id_map[host]
        self.connections[id].add_task(task)

    async def process_task(self):
        while not eos.should_exit():
            try:
                ret = self.priority_index.pop_last()
                if not ret:
                    await asyncio.sleep(0.01)
                    continue
                priority, id = ret
                conn = self.connections[id]
                await conn.process()
                self.priority_index.create(id, conn.relative_priority())
                for conn in self.connections:
                    old_relative_priority = conn.relative_priority()
                    conn.clear_expired(self.window_time)
                    relative_priority = conn.relative_priority()
                    if relative_priority != old_relative_priority:
                        self.priority_index.modify(conn.id, relative_priority)
            except asyncio.exceptions.CancelledError:
                logger.info("Scheduler task cancelled")                
                return

scheduler = WeightedFairScheduler()

def create_schedule_task():
    return asyncio.create_task(scheduler.process_task())

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    client_data = await cache.get(client_ip)
    if client_data is None:
        # New client, start tracking
        client_data = {
            'request_count': 1,
            'start_time': current_time,
            'block_until': 0
        }
    else:
        if current_time < client_data['block_until']:
            # Client is currently blocked, raise an error
            error = '{"code":400, "message":"Too Many Requests, try again later.","error":{"code":0,"name":"","what":"","details":[]}}'
            return PlainTextResponse(error, status_code=400)
        elif current_time - client_data['start_time'] < 60:
            # Less than a minute has passed since first request
            client_data['request_count'] += 1
            if client_data['request_count'] > REQUESTS_PER_MINUTE:
                # Rate limit exceeded, block the client
                client_data['block_until'] = current_time + BLOCK_INTERVAL
                error = '{"code":400, "message":"Too Many Requests, try again later.","error":{"code":0,"name":"","what":"","details":[]}}'
                return PlainTextResponse(error, status_code=400)
        else:
            # More than a minute has passed since first request, reset the counter
            client_data['request_count'] = 1
            client_data['start_time'] = current_time
    # Store the updated client data
    await cache.set(client_ip, client_data)
    task = scheduler.add_task(request.client.host, call_next(request))
    response = await task.wait()
    return response
