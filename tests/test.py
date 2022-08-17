import hashlib
import pytest
from ipyeos import eos

def test_basic():
    key = eos.create_key()
    priv_key = key['private']
    print(eos.get_public_key(priv_key))
    digest = hashlib.sha256(b'Hello World').hexdigest()
    # digest = digest.upper()
    print(digest, priv_key)
    signature = eos.sign_digest(priv_key, digest)
    print(signature)
