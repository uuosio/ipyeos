import os
import asyncio
import secrets
import json
import time
import pickle
import yaml
import pytest
import tempfile

from ipyeos.chaintester import ChainTester
from ipyeos.types import *
from ipyeos import eos, net, log
from ipyeos.transaction import Transaction
from ipyeos import net
from ipyeos.net import HandshakeMessage, ChainSizeMessage, GoAwayMessage, GoAwayReadon, TimeMessage
from ipyeos.net import RequestMessage, NoticeMessage, OrderedIds, IdListModes
from ipyeos.net import SyncRequestMessage
from ipyeos.net import PackedTransactionMessage
from ipyeos.net import Connection, Network

from ipyeos.packer import Encoder, Decoder
from ipyeos import utils
from ipyeos.blocks import BlockHeader
from ipyeos.structs import Symbol, Asset, Transfer
from ipyeos.trace_api import TraceAPI
from ipyeos.database import TableIdObjectIndex, KeyValueObjectIndex
from ipyeos.node import Node

logger = log.get_logger(__name__)
dir_name = os.path.dirname(__file__)
logger.info(dir_name)

def test_chain_size_message():
    # Create a ChainSizeMessage object
    msg = ChainSizeMessage(
        last_irreversible_block_num=1234,
        last_irreversible_block_id=Checksum256.from_string('3db16538f4f6a6698e67805e825121283ccb96a7326ff36d10f727d5a60dd21d'),
        head_num=5678,
        head_id=Checksum256.from_string('fa5b98ece051b7a8438b0364801503396c829a4dd38e3e9e35c3a00e8f56e0ea')
    )

    # Test the __eq__() method with an equal object
    assert msg == ChainSizeMessage(
        last_irreversible_block_num=1234,
        last_irreversible_block_id=Checksum256.from_string('3db16538f4f6a6698e67805e825121283ccb96a7326ff36d10f727d5a60dd21d'),
        head_num=5678,
        head_id=Checksum256.from_string('fa5b98ece051b7a8438b0364801503396c829a4dd38e3e9e35c3a00e8f56e0ea')
    )

    # Test the __eq__() method with a different object
    assert msg != ChainSizeMessage(
        last_irreversible_block_num=1234,
        last_irreversible_block_id=Checksum256.from_string('3db16538f4f6a6698e67805e825121283ccb96a7326ff36d10f727d5a60dd21d'),
        head_num=5678,
        head_id=Checksum256.from_string('9a8b7c6d5e4f3a291b0c1d2e3f405060708090a0b0c0d0e0f101112131415161')
    )

    # Test the pack() and unpack() methods
    enc = Encoder()
    msg.pack(enc)
    raw_msg = enc.get_bytes()
    dec = Decoder(raw_msg)
    assert msg == ChainSizeMessage.unpack(dec)
    msg = eos.unpack_native_object(eos.NativeType.chain_size_message, raw_msg)
    logger.info(msg)

def test_go_away_message():
    # Create a GoAwayMessage object
    msg = GoAwayMessage(
        reason=GoAwayReadon.duplicate,
        node_id=Checksum256.from_string('3db16538f4f6a6698e67805e825121283ccb96a7326ff36d10f727d5a60dd21d')
    )

    # Test the __eq__() method with an equal object
    assert msg == GoAwayMessage(
        reason=GoAwayReadon.duplicate,
        node_id=Checksum256.from_string('3db16538f4f6a6698e67805e825121283ccb96a7326ff36d10f727d5a60dd21d')
    )

    # Test the __eq__() method with a different object
    assert msg != GoAwayMessage(
        reason=GoAwayReadon.duplicate,
        node_id=Checksum256.from_string('9a8b7c6d5e4f3a291b0c1d2e3f405060708090a0b0c0d0e0f101112131415161')
    )

    # Test the pack() and unpack() methods
    enc = Encoder()
    msg.pack(enc)
    dec = Decoder(enc.get_bytes())
    assert msg == GoAwayMessage.unpack(dec)
    msg2 = eos.unpack_native_object(eos.NativeType.go_away_message, enc.get_bytes())
    logger.info(msg2)
    msg2 = json.loads(msg2)
    assert msg2['node_id'] == msg.node_id.to_string() and msg2['reason'] == msg.reason.value

def test_time_message():
    # Create a TimeMessage object
    msg = TimeMessage(
        org=1234567890,
        rec=1234567891,
        xmt=1234567892,
        dst=1234567893
    )

    # Test the __repr__() method
    assert repr(msg) == """TimeMessage(
            org: 1234567890,
            rec: 1234567891,
            xmt: 1234567892,
            dst: 1234567893
        )"""

    # Test the __eq__() method with an equal object
    assert msg == TimeMessage(
        org=1234567890,
        rec=1234567891,
        xmt=1234567892,
        dst=1234567893
    )

    # Test the __eq__() method with a different object
    assert msg != TimeMessage(
        org=1234567890,
        rec=1234567891,
        xmt=1234567892,
        dst=1234567894
    )

    # Test the pack() and unpack() methods
    enc = Encoder()
    msg.pack(enc)
    dec = Decoder(enc.get_bytes())
    assert msg == TimeMessage.unpack(dec)
    msg = eos.unpack_native_object(eos.NativeType.time_message, enc.get_bytes())
    logger.info(msg)

def test_notice_message():
    # Create an OrderedIds object
    ordered_ids = OrderedIds(
        mode=IdListModes.normal,
        pending=1234,
        ids=[Checksum256.from_string('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')]
    )
    # Create a NoticeMessage object
    msg = NoticeMessage(
        known_trx=ordered_ids,
        known_blocks=ordered_ids
    )

    logger.info(msg)

    # Test the __eq__() method with an equal object
    assert msg == NoticeMessage(
        known_trx=ordered_ids,
        known_blocks=ordered_ids
    )

    # Test the __eq__() method with a different object
    assert msg != NoticeMessage(
        known_trx=ordered_ids,
        known_blocks=OrderedIds(
            mode=IdListModes.normal,
            pending=5678,
            ids=[Checksum256.from_string('fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210')]
        )
    )

    ids = {
        "mode": 0,
        "pending": 0xffaabbcc,
        "ids": ["0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"]
    }

    msg = {
        "known_trx": ids,
        "known_blocks": ids
    }

    raw_msg = eos.pack_native_object(eos.NativeType.notice_message, json.dumps(msg))
    logger.info(raw_msg)

    msg = eos.unpack_native_object(eos.NativeType.notice_message, raw_msg)
    logger.info(msg)

    dec = Decoder(raw_msg)
    msg = NoticeMessage.unpack(dec)
    logger.info(msg)
    return

    # Test the pack() and unpack() methods
    enc = Encoder()
    msg.pack(enc)
    dec = Decoder(enc.get_bytes())
    assert msg == NoticeMessage.unpack(dec)
    msg = eos.unpack_native_object(eos.NativeType.notice_message, enc.get_bytes())
    logger.info(msg)

def test_sync_request_message():
    # Create a SyncRequestMessage object
    msg = SyncRequestMessage(
        start_block=1234,
        end_block=5678
    )

    # Test the __repr__() method
    assert repr(msg) == """SyncRequestMessage(
            start_block: 1234,
            end_block: 5678
        )"""

    # Test the __eq__() method with an equal object
    assert msg == SyncRequestMessage(
        start_block=1234,
        end_block=5678
    )

    # Test the __eq__() method with a different object
    assert msg != SyncRequestMessage(
        start_block=1234,
        end_block=5679
    )

    # Test the pack() and unpack() methods
    enc = Encoder()
    msg.pack(enc)
    dec = Decoder(enc.get_bytes())
    assert msg == SyncRequestMessage.unpack(dec)

def test_handshake_message():
    msg = HandshakeMessage(
        network_version=123,
        chain_id=Checksum256(bytes.fromhex('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')),
        node_id=Checksum256(bytes.fromhex('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')),
        key=PublicKey(bytes.fromhex('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef1122')),
        time=1234567890,
        token=Checksum256(bytes.fromhex('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')),
        sig=Signature.emtpy(),
        p2p_address='127.0.0.1:9876',
        last_irreversible_block_num=123456,
        last_irreversible_block_id=Checksum256(bytes.fromhex('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')),
        head_num=123457,
        head_id=Checksum256(bytes.fromhex('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')),
        os='Linux',
        agent='ipyeos',
        generation=123
    )
    logger.info(msg)
    enc = Encoder()
    msg.pack(enc)
    raw_msg = enc.get_bytes()

    msg2 = HandshakeMessage.unpack(Decoder(raw_msg))
    assert msg == msg2
    msg3 = eos.unpack_native_object(eos.NativeType.handshake_message, raw_msg)
    assert msg.generation == json.loads(msg3)['generation']

def test_block_header():
    raw_block = b'^~ZX\x00\x00\x00\x00\x00\xea0U\x00\x00\x00\x00\x03\xe7\xa9\xdc"\xf6\x98\xe6z\x83\xb0Q\x06\x81\xab\x9b\xe6\xb5\xd3\x01"\x9f\xad\xed\xcd\xd69/e\x98\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd3\'\xe3\xf0"P6\x9e8\xe3:\x8d\x01\xce!\x18\xda\xb4^\xc1!\xbb\xf6X\x8e\x89\xbd\x7f@\xf6&\xfe\x00\x00\x00\x00\x00\x00\x00  \xe2\x02\xe6\x90A?{7H\xe2*\\!\x04Rm\xb3\x0e\xc5\x1e]u\xbcuq\x8d\xa1\xd3\xa1\x19\xcc#G\xa3\xe5Yc\xbd\xda^\x85\xb7r\xb7\xb9W\xbd\xa9h\xb0\x7f,\xba\xc8<\xba\xb9\xf8c\x8ds\xf9\xf5\x00\x00'
    block = BlockHeader.unpack_bytes(raw_block)
    logger.info(block)
    logger.info(eos.unpack_block(raw_block))

# print(os.getpid())
# input('Press enter to continue: ')

def test_config_file():
    with open('./data/config.yaml') as f:
        config = yaml.safe_load(f)
    logging_config_file = config['logging_config_file']
    chain_config = config['chain_config']
    state_size=chain_config['state_size']
    data_dir = chain_config['data_dir']
    config_dir = chain_config['config_dir']
    genesis = config['genesis']
    print(json.dumps(genesis, indent=4))

def test_connection():
    with open('./data/config.yaml') as f:
        config = yaml.safe_load(f)
    logging_config_file = config['logging_config_file']
    chain_config = config['chain_config']
    state_size=chain_config['state_size']
    data_dir = chain_config['data_dir']
    config_dir = chain_config['config_dir']

    peers = config['peers']
    logger.error(f'peers: {peers}')
    for peer in peers:
        if peers.count(peer) > 1:
            logger.error(f'duplicated peer: {peer}')
            return

    genesis = config['genesis']

    node = Node(False, data_dir=data_dir, config_dir=config_dir, genesis = genesis, state_size=state_size)
    # trace = TraceAPI(node.chain, 'dd/trace')

    # trace = trace.get_block_trace(10)

    node.chain.abort_block()
    print(node.chain.chain_id())
    # peer.eosio.sg:9876
    # eu1.eosdac.io:49876
    network = Network(node.chain, config['peers'])
    # network = Network(node.chain, 'peer.main.alohaeos.com', '9876')
    try:
        asyncio.run(network.run())
    except KeyboardInterrupt:
        pass

def test_snapshot():
    data_dir = tempfile.mkdtemp()
    config_dir = tempfile.mkdtemp()
    snapshot_file = './data/snapshot-0000001ba25b3b5af4ba6cacecb68ef4238a50bb7134e56fe985b4355fbf7488.bin'
    node = Node(False, data_dir=data_dir, config_dir=config_dir, genesis = None, state_size=10*1024*1024, snapshot_file=snapshot_file, log_level=5)
    assert node.chain.head_block_num() == 27

async def run_time_message_test(peer):
    host, port = peer.split(':')
    reader, writer = await asyncio.open_connection(host, port)
    conn = Connection(reader, writer)
    count = 10
    total_delay = 0.0
    for i in range(count):
        org = int(time.time()*1e9)
        last_time_message = TimeMessage(0, 0, org, 0)
        await conn.send_message(last_time_message)

        tp, raw_msg = await conn.read_message()
        if not raw_msg:
            break
        if not tp == net.time_message:
            print(tp, raw_msg)
            continue
        message = TimeMessage.unpack_bytes(raw_msg)
        # logger.info(message)
        now_time = int(time.time()*1e9)
        if not message.is_valid():
            logger.info("invalid time message")
            continue
        if last_time_message and last_time_message.xmt == message.org:
            message.dst = now_time
            delay = (message.dst - message.org)
            # logger.info("delay: %s", delay/1e9)
            total_delay += delay/1e9
    print(f"avg delay of {host}:{port}: {total_delay/count}")

@pytest.mark.asyncio
async def test_time_message():
    peers = [
        "peer.main.alohaeos.com:9876",
        "bp.cryptolions.io:9876",
        "p2p.eosdetroit.io:3018",
        "peer.eosn.io:9876",
        "boot.eostitan.com:9876",
        "peer.eosio.sg:9876",
    ]
    tasks = []
    for peer in peers:
        task = asyncio.create_task(run_time_message_test(peer))
        tasks.append(task)

    await asyncio.gather(*tasks)
