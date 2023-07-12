import asyncio

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from .uvicorn_server import UvicornServer

app = FastAPI()

class Item(BaseModel):
    code: str

def read_root():
    """
    Returns a JSON object with a single key-value pair: "Hello" -> "World".
    """
    return {"Hello": "World"}

def init(port: int=8088):
    app.get("/")(read_root)
    config = uvicorn.Config(app, host="127.0.0.1", port=port)
    server = UvicornServer(config)
    return server

async def start(server):
    await server.serve()

if __name__ == '__main__':
    asyncio.run(run(8088))
