from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer
import time
from . import log

cache = Cache(Cache.MEMORY, serializer=PickleSerializer())

REQUESTS_PER_MINUTE = 100
BLOCK_INTERVAL = 60 # Block for 1 minute if the limit is exceeded

logger = log.get_logger(__name__)

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

    # Proceed with the request
    response = await call_next(request)
    return response
