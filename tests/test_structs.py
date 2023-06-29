import json
import time
from ipyeos import log, eos
from ipyeos.net import HandshakeMessage
from ipyeos.packer import Encoder, Decoder
from ipyeos.structs import Symbol, Asset, Transfer

logger = log.get_logger(__name__)

def test_transfer():
    a = Asset(1000000, Symbol(4, 'EOS'))
    t = Transfer('eosio', 'alice', a, 'test transfer')
    enc = Encoder()
    t.pack(enc)
    dec = Decoder(enc.get_bytes())
    t2 = Transfer.unpack(dec)
    assert t == t2
