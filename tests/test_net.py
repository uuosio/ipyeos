import os
import asyncio
import secrets
import json
import time

from ipyeos.types import *
from ipyeos import eos, net, log
from ipyeos.net import HandshakeMessage, ChainSizeMessage, GoAwayMessage, GoAwayReadon, TimeMessage
from ipyeos.net import RequestMessage, NoticeMessage, OrderedIds, IdListModes
from ipyeos.net import SyncRequestMessage
from ipyeos.net import Connection
from ipyeos.chaintester import ChainTester

from ipyeos.packer import Encoder, Decoder
from ipyeos import utils
from ipyeos.blocks import BlockHeader

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

def build_handshake_message(t):
    msg = HandshakeMessage(
        network_version=123,
        chain_id=Checksum256(bytes.fromhex('8a34ec7df1b8cd06ff4a8abbaa7cc50300823350cadc59ab296cb00d104d2b8f')),
        node_id=Checksum256(bytes.fromhex('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')),
        key=PublicKey(b'\x00'*34),
        time=int(time.time()*1e9),
        token=Checksum256.empty(),
        sig=Signature.empty(),
        p2p_address='127.0.0.1:9876',
        last_irreversible_block_num=t.chain.last_irreversible_block_num,
        last_irreversible_block_id=t.chain.last_irreversible_block_id,
        head_num=t.chain.head_block_num,
        head_id=Checksum256.empty(),
        os='Linux',
        agent='ipyeos',
        generation=0
    )
    return msg
# print(os.getpid())
# input('press enter to continue')

def test_connection():
    t = ChainTester(False, data_dir=os.path.join(dir_name, 'dd'), config_dir=os.path.join(dir_name, 'cd'), log_level=5)
    action = ['eosio', 'sayhello', b'hello, world', {'eosio':'active'}]
    tx = t.gen_transaction([action], json_str=True)
    logger.info(tx)

    tx = t.gen_transaction([action], json_str=False, compress=True)
    logger.info(eos.unpack_transaction(tx))
    return
    t.chain.abort_block()
    print()
    async def run():
        reader, writer = await asyncio.open_connection('127.0.0.1', 9100)
        conn = Connection(reader, writer)
        async def heart_beat():
            while True:
                await asyncio.sleep(10.0)
                msg = TimeMessage(0, 0, int(time.time()*1e9), 0)
                # logger.info(msg)
                conn.send_message(msg)
        asyncio.ensure_future(heart_beat())
        msg = build_handshake_message(t)

        # logger.info(msg.pack_message())
        # msg = SyncRequestMessage(100, 200)
        # logger.info(msg.pack_message())
        conn.send_message(msg)
        head_block_num = 0
        last_handshake = None

        while True:
            tp, raw_msg = await conn.read_message()
            if not raw_msg:
                break
            if tp == net.handshake_message:
                message = HandshakeMessage.unpack_bytes(raw_msg)
                last_handshake = message
                logger.info(message)
                head_block_num = message.head_num
                start_block = t.chain.head_block_num + 1
                logger.info("+++++start_block: %s", start_block)
                if start_block < message.head_num:
                    conn.send_message(SyncRequestMessage(start_block, message.head_num))
                elif message.head_num == t.chain.head_block_num:
                    # last_irr_catch_up catch_up
                    logger.info('+++++++sync finished, request catch up')
                    req_trx = OrderedIds(net.IdListModes.none, 0, [])
                    req_blocks = OrderedIds(net.IdListModes.catch_up, t.chain.head_block_num, [])
                    msg = RequestMessage(req_trx, req_blocks)
                    logger.info(msg)

                # conn.send_message(SyncRequestMessage(start_block=2, end_block=10))
            elif tp == net.go_away_message:
                message = GoAwayMessage.unpack_bytes(raw_msg)
                logger.info(message)
                break
            elif tp == net.request_message:
                message = RequestMessage.unpack_bytes(raw_msg)
                logger.info(message)
            elif tp == net.signed_block:
                header = BlockHeader.unpack_bytes(raw_msg)
                received_block_num = header.block_num
                head_block_num = t.chain.head_block_num
                logger.info("++++++++head_block_num: %s, received_block_num: %s", head_block_num, received_block_num)
                if not head_block_num +1 == received_block_num:
                    logger.info("++++++++++invalid incomming block number: %s: %s", head_block_num, received_block_num)
                    continue
                ret = t.chain.push_raw_block(raw_msg)
                assert ret
                # if received_block_num % 100 == 0:
                #     logger.info("%s", raw_msg)
                #     msg = eos.unpack_block(raw_msg)
                #     msg = json.loads(msg)
                #     logger.info("%s", msg)
                #     logger.info("++++++++++%s: %s", received_block_num, head_block_num)
                if last_handshake.head_num == received_block_num:
                    msg = build_handshake_message(t)
                    conn.send_message(msg)
            elif tp == net.time_message:
                message = TimeMessage.unpack_bytes(raw_msg)
                logger.info(message)
                now_time = int(time.time()*1e9)
                if not message.is_valid():
                    logger.info("invalid time message")
                    continue
                reply_message = TimeMessage(message.xmt, message.dst, now_time, 0)
                conn.send_message(message)
            elif tp == net.sync_request_message:
                message = SyncRequestMessage.unpack_bytes(raw_msg)
                logger.info(message)
            else:
                print(tp, raw_msg)

    async def try_run():
        try:
            await run()
        except asyncio.exceptions.CancelledError:
            logger.info("CancelledError")
            t.free()

    try:
        asyncio.run(try_run())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")
        t.free()
