import json
import time

from ipyeos import eos
from ipyeos.bases import log
from ipyeos.node.messages import HandshakeMessage
from ipyeos.bases.packer import Encoder, Decoder
from ipyeos.bases.types import Checksum256, PublicKey, PrivateKey, Signature

logger = log.get_logger(__name__)

def test_public_key():
    s = 'EOS5NWQwMDmL2yXgnohEBa7FqvdevaLY6Wf1bnoa3unnTWPqrX5YD'
    pub = PublicKey.from_base58(s)
    assert s == pub.to_base58()

def test_signature():
    s = 'SIG_K1_Jxpdg9R5QsrAZ25HM6DWwZgfDHvSw2QMBRXRyiDC2HdKHzu4q5aCLXWeuzWwUCwSv3tATt2tjR8a1T2gzzDj7FijhoD6Ms'
    sig = Signature.from_base58(s)
    s2 = sig.to_base58()
    assert s == s2

def test_private_key():
    base58_priv_key = '5JRYimgLBrRLCBAcjHUWCYRv3asNedTYYzVgmiU4q2ZVxMBiJXL'
    priv_key = PrivateKey.from_base58(base58_priv_key)
    logger.info(priv_key.to_base58() == base58_priv_key)

def test_name():
    count = 1000000
    start = time.monotonic()
    for n in range(count):
        name = eos.s2b('zzzzzzzzzzzzj')
    end = time.monotonic()
    logger.info("%s", count/(end - start))

def test_checksum256():
    a = Checksum256(b'\x00' * 32)
    print(a.to_string())
    print(a.to_bytes())
