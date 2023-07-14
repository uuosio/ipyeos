import asyncio

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from .uvicorn_server import UvicornServer
from . import net, node

app = FastAPI()

class Item(BaseModel):
    code: str

class PushTransactionArgs(BaseModel):
    """
    A Pydantic model that represents the arguments for the `push_transaction` RPC method.

    Attributes:
        packed_tx: A hex string that contains the packed transaction data.
        Related C++ struct:
        ```C++
        struct packed_transaction : fc::reflect_init {
        private:
            vector<signature_type>                  signatures;
            fc::enum_type<uint8_t,compression_type> compression;
            bytes                                   packed_context_free_data;
            // transaction (not signed_transaction) packed and possibly compressed according to compression
            bytes                                   packed_trx;
        };
        ```
    """
    packed_tx: str
    speculate: bool = False

async def read_root():
    """
    Returns a JSON object with a single key-value pair: "Hello" -> "World".
    """
    return {"Hello": "World"}

@app.get("/get_info", response_class=PlainTextResponse)
async def get_info():
    return node.get_node().api.get_info(is_json=False)

@app.post("/push_transaction")
async def push_transaction(args: PushTransactionArgs):
    """
    Sends a packed transaction to the network.

    Args:
        args: An instance of the PushTransactionArgs model that contains the packed transaction data.

    Returns:
        The response from the network.
    """
    packed_tx = bytes.fromhex(args.packed_tx)
    msg = net.PackedTransactionMessage(packed_tx)
    return await node.get_network().conn.send_message(msg)

def init(port: int=8088):
    app.get("/")(read_root)
    config = uvicorn.Config(app, host="127.0.0.1", port=port)
    server = UvicornServer(config)
    return server

async def start(server):
    await server.serve()

if __name__ == '__main__':
    asyncio.run(run(8088))
