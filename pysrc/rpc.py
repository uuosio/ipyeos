import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from .uvicorn_server import UvicornServer

app = FastAPI()

class Item(BaseModel):
    code: str

@app.get("/")
def read_root():
    """
    Returns a JSON object with a single key-value pair: "Hello" -> "World".
    """
    return {"Hello": "World"}

def init(port: int=8088):
    config = uvicorn.Config(app, host="127.0.0.1", port=port)
    server = UvicornServer(config)
    return server

async def start(server):
    await server.serve()

if __name__ == '__main__':
    asyncio.run(run(8088))
