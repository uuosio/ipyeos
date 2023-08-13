import asyncio
import ipaddress
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer
from queue import PriorityQueue

from . import eos, log
from .multi_index import key_u64_value_double_index, secondary_double_index

cache = Cache(Cache.MEMORY, serializer=PickleSerializer())

MAX_CONNECTIONS = 1000
REQUESTS_PER_MINUTE = 100
BLOCK_INTERVAL = 60 # Block for 1 minute if the limit is exceeded

logger = log.get_logger(__name__)

class Task(object):
    def __init__(self, url, task):
        self.task = task
        self.url = url
        self.event = asyncio.Event()
        self.ret = None

    async def run(self):
        try:
            self.ret = await self.task
        except Exception as e:
            logger.exception(e)
            self.ret = e
        self.event.set()
        return self.ret

    async def wait(self):
        await self.event.wait()
        return self.ret

class Connection:
    def __init__(self, id, host, weight=1, clear_expired_served_time=False):
        self.id = id
        self.host = host
        self.tasks = []
        self.weight = weight
        self.served_time = 0
        self.served_times = key_u64_value_double_index()
        self.clear_expired_served_time = clear_expired_served_time

    def __repr__(self):
        return f"Connection id: {self.id} host: {self.host} weight: {self.weight} served_time: {self.served_time} tasks: {self.tasks}"

    def __str__(self):
        return repr(self)

    async def process(self):
        if not self.tasks:
            return None
        task = self.tasks.pop(0)
        logger.debug(f"Processing task {task.task} for {self.host} {task.url}")
        start = time.monotonic()
        ret = await task.run()
        duration = time.monotonic() - start
        self.served_time += duration
        return ret

    def add_task(self, url, task):
        _task = Task(url, task)
        self.tasks.append(_task)
        return _task
    
    def clear_expired(self, window_time):
        current_time = int(time.time())
        while True:
            ret = self.served_times.first()
            if not ret:
                break
            time_slot, duration = ret
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
    def __init__(self, window_time = 30):
        self.connections = {}
        self.priority_index = secondary_double_index()
        self.last_task_time_index = secondary_double_index()
        self.window_time = window_time #60*10
        self.clear_inactive_connections_time = time.monotonic()

    def add_task(self, host, url, task):
        if len(self.connections) >= MAX_CONNECTIONS:
            return None
        int_address = int(ipaddress.ip_address(host))
        conn = None
        try:
            conn = self.connections[int_address]
        except KeyError:
            conn = Connection(int_address, host)
            self.connections[int_address] = conn
        task = conn.add_task(url, task)
        self.priority_index.set(int_address, conn.relative_priority())
        self.last_task_time_index.set(int_address, time.monotonic())
        return task

    def clear_inactive_connections(self):
        if time.monotonic() - self.clear_inactive_connections_time < 30:
            if len(self.connections) < MAX_CONNECTIONS:
                return
        self.clear_inactive_connections_time = time.monotonic()
        while True:
            ret = self.last_task_time_index.first()
            if not ret:
                break
            id, last_task_time = ret
            if time.monotonic() - last_task_time < self.window_time:
                break
            self.last_task_time_index.pop_first()
            self.priority_index.remove(id)
            conn = self.connections[id]
            del self.connections[id]
            logger.info("Removing inactive connection %s", conn)

    async def _process_task(self):
        self.clear_inactive_connections()
        ret = self.priority_index.last()
        if not ret:
            await asyncio.sleep(0.01)
            return
        id, priority = ret
        conn = self.connections[id]
        if not conn.tasks:
            await asyncio.sleep(0.01)
            return
        logger.debug(f"Processing connection {conn}")
        ret = await conn.process()
        if not ret:
            return
        self.priority_index.set(id, conn.relative_priority())
        return ret

    async def process_task(self):
        while not eos.should_exit():
            try:
                await self._process_task()
            except asyncio.exceptions.CancelledError:
                logger.info("Scheduler task cancelled")
                return
            except Exception as e:
                logger.exception(e)
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
    task = scheduler.add_task(request.client.host, request.url, call_next(request))
    if not task:
        error = '{"code":400, "message":"Too Many Connections, try again later.","error":{"code":0,"name":"","what":"","details":[]}}'
        return PlainTextResponse(error, status_code=400)
    logger.debug("+++++++= Waiting for task %s", task)
    response = await task.wait()
    logger.debug("+++++++= Got response for task %s", response)
    return response
