import os
import glob
import sys
import json
import time
import traceback
import logging

from typing import NewType, Dict, Optional
i32 = NewType('i32', int)
i64 = NewType('i64', int)
u64 = NewType('u64', int)

Iterator = NewType('Iterator', i32)

from .interfaces import IPCChainTester, ApplyRequest, Apply

from .interfaces.ttypes import Uint64, DataBuffer, NextPreviousReturn,FindPrimaryReturn, FindSecondaryReturn, LowerBoundUpperBoundReturn

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.protocol.THeaderProtocol import THeaderProtocolFactory
from thrift.Thrift import TType, TMessageType, TApplicationException

from . import chaintester 
from . import eos, _vm_api, log
from .chaintester import ChainTester

chaintester.chain_config['contracts_console'] = True

logger = log.get_logger(__name__)
logger.setLevel(logging.DEBUG)

def to_uint64(value):
    return Uint64(int.to_bytes(value, 8, 'little'))

def from_uint64(value):
    assert len(value.rawValue) == 8, 'bad Uint64'
    return int.from_bytes(value.rawValue, 'little')

class EndApplyException(Exception):
    pass

class VMAPIHandler:
    def end_apply(self):
        return 1

    def prints(self, msg):
        _vm_api.prints(msg)

#void prints_l( const char* cstr, uint32_t len);
    def prints_l(self, cstr: bytes):
        _vm_api.prints_l(cstr)

    def printi(self, n: i64):
        _vm_api.printi(n)

    def printui(self, n: Uint64):
        _vm_api.printui(n.into())

    # void printi128( const int128_t* value );
    def printi128(self, value: bytes):
        _vm_api.printi128(value)

    # void printui128( const uint128_t* value );
    def printui128(self, value: bytes):
        _vm_api.printui128(value)

    # void printsf(float value);
    def printsf(self, value: bytes):
        _vm_api.printsf(value)

    # void printdf(double value);
    def printdf(self, value: bytes):
        _vm_api.printdf(value)

    # void printqf(const long double* value);
    def printqf(self, value: bytes):
        _vm_api.printqf(value)

    # void printn( uint64_t name );
    def printn(self, name: Uint64):
        _vm_api.printn(name.into())

    # void printhex( const void* data, uint32_t datalen );
    def printhex(self, data: bytes):
        _vm_api.printhex(data)

    def action_data_size(self):
        return _vm_api.action_data_size()

    def read_action_data(self):
        return _vm_api.read_action_data()

    # void require_recipient( uint64_t name );
    def require_recipient(self, name: Uint64):
        _vm_api.require_recipient(name.into())

    # void require_auth( uint64_t name );
    def require_auth(self, name: Uint64):
        _vm_api.require_auth(name.into())

    # bool has_auth( uint64_t name );
    def has_auth(self, name: Uint64):
        return _vm_api.has_auth(name.into())

    # void require_auth2( uint64_t name, uint64_t permission );
    def require_auth2(self, name: Uint64, permission: Uint64):
        _vm_api.require_auth2(name.into(), permission.into())

    # bool is_account( uint64_t name );
    def is_account(self, name: Uint64):
        return _vm_api.is_account(name.into())

    def send_inline(self, serialized_data):
        _vm_api.send_inline(serialized_data)

    def send_context_free_inline(self, serialized_data: bytes):
        _vm_api.send_inline(serialized_data)

    # uint64_t  publication_time();
    def publication_time(self):
        ret = _vm_api.publication_time()
        return to_uint64(ret)

    # uint64_t current_receiver();
    def current_receiver(self, ):
        ret = _vm_api.current_receiver()
        return to_uint64(ret)

    # void  eosio_assert( uint32_t test, const char* msg );
    def eosio_assert(self, test, msg: bytes):
        _vm_api.eosio_assert(test, msg)

    # void  eosio_assert_message( uint32_t test, const char* msg, uint32_t msg_len );
    def eosio_assert_message(self, test, msg: bytes):
        _vm_api.eosio_assert_message(test, msg)

    # void  eosio_assert_code( uint32_t test, uint64_t code );
    def eosio_assert_code(self, test, code):
        _vm_api.eosio_assert_code(test, code.into())

    # void eosio_exit( int32_t code );
    def eosio_exit(self, code: i32):
        _vm_api.eosio_exit(code)

    # uint64_t  current_time();
    def current_time(self):
        ret = _vm_api.current_time()
        return to_uint64(ret)

    # bool is_feature_activated( const capi_checksum256* feature_digest );
    def is_feature_activated(self, feature_digest: bytes):
        return _vm_api.is_feature_activated(feature_digest)

    # uint64_t get_sender();
    def get_sender(self):
        ret = _vm_api.get_sender()
        return to_uint64(ret)

    # void assert_sha256( const char* data, uint32_t length, const capi_checksum256* hash );
    def assert_sha256(self, data: bytes, hash: bytes):
        _vm_api.assert_sha256(data, hash)

    # void assert_sha1( const char* data, uint32_t length, const capi_checksum160* hash );
    def assert_sha1(self, data: bytes, hash: bytes):
        _vm_api.assert_sha1(data, hash)

    # void assert_sha512( const char* data, uint32_t length, const capi_checksum512* hash );
    def assert_sha512(self, data: bytes, hash: bytes):
        _vm_api.assert_sha512(data, hash)

    # void assert_ripemd160( const char* data, uint32_t length, const capi_checksum160* hash );
    def assert_ripemd160(self, data: bytes, hash: bytes):
        _vm_api.assert_ripemd160(data, hash)

    # void sha256( const char* data, uint32_t length, capi_checksum256* hash );
    def sha256(self, data: bytes):
        return _vm_api.sha256(data)

    # void sha1( const char* data, uint32_t length, capi_checksum160* hash );
    def sha1(self, data: bytes):
        return _vm_api.sha1(data)

    # void sha512( const char* data, uint32_t length, capi_checksum512* hash );
    def sha512(self, data: bytes):
        return _vm_api.sha512(data)

    # void ripemd160( const char* data, uint32_t length, capi_checksum160* hash );
    def ripemd160(self, data: bytes):
        return _vm_api.ripemd160(data)

    # int32_t recover_key( const capi_checksum256* digest, const char* sig, uint32_t siglen, char* pub, uint32_t publen );
    def recover_key(self, digest: bytes, sig: bytes):
        return _vm_api.recover_key(digest, sig)

    # void assert_recover_key( const capi_checksum256* digest, const char* sig, uint32_t siglen, const char* pub, uint32_t publen );
    def assert_recover_key(self, digest: bytes, sig: bytes, pub: bytes):
        _vm_api.assert_recover_key(digest, sig, pub)


    #transaction.h
    # void send_deferred(const uint128_t sender_id, uint64_t payer, const char *serialized_transaction, uint32_t size, uint32_t replace_existing = 0);
    def send_deferred(self, sender_id: bytes, payer: Uint64, serialized_transaction: bytes, replace_existing: i32):
        _vm_api.send_deferred(sender_id, payer.into(), serialized_transaction, replace_existing)

    # int32_t cancel_deferred(const uint128_t sender_id);
    def cancel_deferred(self, sender_id: bytes):
        return _vm_api.cancel_deferred(sender_id)

    # uint32_t read_transaction(char *buffer, uint32_t size);
    def read_transaction(self):
        return _vm_api.read_transaction()

    # uint32_t transaction_size();
    def transaction_size(self):
        return _vm_api.transaction_size()

    # int32_t tapos_block_num();
    def tapos_block_num(self):
        return _vm_api.tapos_block_num()

    # int32_t tapos_block_prefix();
    def tapos_block_prefix(self):
        return _vm_api.tapos_block_prefix()

    # uint32_t expiration();
    def expiration(self):
        return _vm_api.expiration()

    # int32_t get_action( uint32_t type, uint32_t index, char* buff, uint32_t size );
    def get_action(self, _type: i32, index: i32):
        return _vm_api.get_action(_type, index)

    # int32_t get_context_free_data( uint32_t index, char* buff, uint32_t size );
    def get_context_free_data(self, index: i32):
        return _vm_api.get_action(index)

    def db_store_i64(self, scope: Uint64, table: Uint64, payer: Uint64, id: Uint64, data: bytes):
        return _vm_api.db_store_i64(scope.into(), table.into(), payer.into(), id.into(), data)

    def db_update_i64(self, iterator: i32, payer: Uint64, data: bytes):
        return _vm_api.db_update_i64(iterator, payer.into(), data)

    def db_remove_i64(self, iterator: i32):
        return _vm_api.db_remove_i64(iterator)

    def db_get_i64(self, iterator: i32):
        return _vm_api.db_get_i64(iterator)

    def db_next_i64(self, iterator: i32):
        it, primary = _vm_api.db_next_i64(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    def db_previous_i64(self, iterator: i32):
        it, primary = _vm_api.db_previous_i64(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    def db_find_i64(self, code: Uint64, scope: Uint64, table: Uint64, id: Uint64):
        return _vm_api.db_find_i64(code.into(), scope.into(), table.into(), id.into())

    def db_lowerbound_i64(self, code: Uint64, scope: Uint64, table: Uint64, id: Uint64):
        return _vm_api.db_lowerbound_i64(code.into(), scope.into(), table.into(), id.into())

    def db_upperbound_i64(self, code: Uint64, scope: Uint64, table: Uint64, id: Uint64):
        return _vm_api.db_upperbound_i64(code.into(), scope.into(), table.into(), id.into())

    def db_end_i64(self, code: Uint64, scope: Uint64, table: Uint64):
        return _vm_api.db_end_i64(code.into(), scope.into(), table.into())

    def db_idx64_store(self, scope: Uint64, table: Uint64, payer: Uint64, id: Uint64, secondary: Uint64) -> i32:
        return _vm_api.db_idx64_store(scope.into(), table.into(), payer.into(), id.into(), secondary.into())

    def db_idx64_update(self, iterator: i32, payer: Uint64, secondary: Uint64):
        _vm_api.db_idx64_update(iterator, payer.into(), secondary.into())

    def db_idx64_remove(self, iterator: i32) -> i32:
        _vm_api.db_idx64_remove(iterator)

    def db_idx64_next(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx64_next(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    def db_idx64_previous(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx64_previous(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    def db_idx64_find_primary(self, code: Uint64, scope: Uint64, table: Uint64, primary: Uint64) -> FindPrimaryReturn:
        it, secondary = _vm_api.db_idx64_find_primary(code.into(), scope.into(), table.into(), primary.into())
        return FindPrimaryReturn(it, secondary)

    def db_idx64_find_secondary(self, code: Uint64, scope: Uint64, table: Uint64, secondary: Uint64) -> FindSecondaryReturn:
        it, primary = _vm_api.db_idx64_find_secondary(code.into(), scope.into(), table.into(), secondary.into())
        return FindSecondaryReturn(it, to_uint64(primary))

    def db_idx64_lowerbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary: Uint64, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx64_lowerbound(code.into(), scope.into(), table.into(), secondary.into(), primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    def db_idx64_upperbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary, primary):
        it, secondary, primary = _vm_api.db_idx64_upperbound(code.into(), scope.into(), table.into(), secondary.into(), primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    def db_idx64_end(self, code: Uint64, scope: Uint64, table: Uint64):
        return _vm_api.db_idx64_end(code.into(), scope.into(), table.into())

    def db_idx128_store(self, scope: Uint64, table: Uint64, payer: Uint64, id, secondary: bytes):
        return _vm_api.db_idx128_store(scope.into(), table.into(), payer.into(), id.into(), secondary)

    def db_idx128_update(self, iterator: i32, payer: Uint64, secondary: bytes):
        return _vm_api.db_idx128_update(iterator, payer.into(), secondary)

    def db_idx128_remove(self, iterator: i32):
        _vm_api.db_idx128_remove(iterator)

    def db_idx128_next(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx128_next(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    def db_idx128_previous(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx128_previous(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    def db_idx128_find_primary(self, code: Uint64, scope: Uint64, table: Uint64, primary: Uint64):
        it, secondary = _vm_api.db_idx128_find_primary(code.into(), scope.into(), table.into(), primary.into())
        return FindPrimaryReturn(it, secondary)

    def db_idx128_find_secondary(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes) -> FindSecondaryReturn:
        it, primary = _vm_api.db_idx128_find_secondary(code.into(), scope.into(), table.into(), secondary)
        return FindSecondaryReturn(it, to_uint64(primary))

    def db_idx128_lowerbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx128_lowerbound(code.into(), scope.into(), table.into(), secondary, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    def db_idx128_upperbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx128_upperbound(code.into(), scope.into(), table.into(), secondary, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    def db_idx128_end(self, code: Uint64, scope: Uint64, table: Uint64):
        return _vm_api.db_idx128_end(code.into(), scope.into(), table.into())

    def db_idx256_store(self, scope: Uint64, table: Uint64, payer: Uint64, id: Uint64, data: bytes) -> i32:
        return _vm_api.db_idx256_store(scope.into(), table.into(), payer.into(), id.into(), data)

    def db_idx256_update(self, iterator: i32, payer: Uint64, data: bytes):
        return _vm_api.db_idx256_update(iterator, payer.into(), data)

    def db_idx256_remove(self, iterator: i32):
        _vm_api.db_idx256_remove(iterator)

    def db_idx256_next(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx256_next(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    def db_idx256_previous(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx256_previous(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    def db_idx256_find_primary(self, code: Uint64, scope: Uint64, table: Uint64, primary: Uint64):
        it, secondary = _vm_api.db_idx256_find_primary(code.into(), scope.into(), table.into(), primary.into())
        return FindPrimaryReturn(it, secondary)

    def db_idx256_find_secondary(self, code: Uint64, scope: Uint64, table: Uint64, data: bytes) -> FindSecondaryReturn:
        it, primary = _vm_api.db_idx256_find_secondary(code.into(), scope.into(), table.into(), data)
        return FindSecondaryReturn(it, to_uint64(primary))

    def db_idx256_lowerbound(self, code: Uint64, scope: Uint64, table: Uint64, data: bytes, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx256_lowerbound(code.into(), scope.into(), table.into(), data, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    def db_idx256_upperbound(self, code: Uint64, scope: Uint64, table: Uint64, data, primary):
        it, secondary, primary = _vm_api.db_idx256_upperbound(code.into(), scope.into(), table.into(), data, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    def db_idx256_end(self, code: Uint64, scope: Uint64, table: Uint64):
        return _vm_api.db_idx256_end(code.into(), scope.into(), table.into())

    def db_idx_double_store(self, scope: Uint64, table: Uint64, payer: Uint64, id: Uint64, secondary: bytes):
        return _vm_api.db_idx_double_store(scope.into(), table.into(), payer.into(), id.into(), secondary)

    def db_idx_double_update(self, iterator: i32, payer: Uint64, secondary: bytes):
        return _vm_api.db_idx_double_update(iterator, payer.into(), secondary)

    def db_idx_double_remove(self, iterator: i32):
        _vm_api.db_idx_double_remove(iterator)

    def db_idx_double_next(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx_double_next(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    def db_idx_double_previous(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx_double_previous(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    def db_idx_double_find_primary(self, code: Uint64, scope: Uint64, table: Uint64, primary: Uint64):
        it, secondary = _vm_api.db_idx_double_find_primary(code.into(), scope.into(), table.into(), primary.into())
        return FindPrimaryReturn(it, secondary)

    def db_idx_double_find_secondary(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes) -> FindSecondaryReturn:
        it, primary = _vm_api.db_idx_double_find_secondary(code.into(), scope.into(), table.into(), secondary)
        return FindSecondaryReturn(it, to_uint64(primary))

    def db_idx_double_lowerbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx_double_lowerbound(code.into(), scope.into(), table.into(), secondary, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    def db_idx_double_upperbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx_double_upperbound(code.into(), scope.into(), table.into(), secondary, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    def db_idx_double_end(self, code: Uint64, scope: Uint64, table: Uint64):
        return _vm_api.db_idx_double_end(code.into(), scope.into(), table.into())

    def db_idx_long_double_store(self, scope: Uint64, table: Uint64, payer: Uint64, id: Uint64, secondary: bytes):
        return _vm_api.db_idx_long_double_store(scope.into(), table.into(), payer.into(), id.into(), secondary)

    def db_idx_long_double_update(self, iterator: i32, payer: Uint64, secondary: bytes):
        return _vm_api.db_idx_long_double_update(iterator, payer.into(), secondary)

    def db_idx_long_double_remove(self, iterator: i32):
        _vm_api.db_idx_long_double_remove(iterator)

    def db_idx_long_double_next(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx_long_double_next(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    def db_idx_long_double_previous(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx_long_double_previous(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    def db_idx_long_double_find_primary(self, code: Uint64, scope: Uint64, table: Uint64, primary: Uint64):
        it, secondary = _vm_api.db_idx_long_double_find_primary(code.into(), scope.into(), table.into(), primary.into())
        return FindPrimaryReturn(it, secondary)

    def db_idx_long_double_find_secondary(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes) -> FindSecondaryReturn:
        it, primary = _vm_api.db_idx_long_double_find_secondary(code.into(), scope.into(), table.into(), secondary)
        return FindSecondaryReturn(it, to_uint64(primary))

    def db_idx_long_double_lowerbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx_long_double_lowerbound(code.into(), scope.into(), table.into(), secondary, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    def db_idx_long_double_upperbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx_long_double_upperbound(code.into(), scope.into(), table.into(), secondary, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    def db_idx_long_double_end(self, code: Uint64, scope: Uint64, table: Uint64):
        return _vm_api.db_idx_long_double_end(code.into(), scope.into(), table.into())

class ApplyRequestClient(ApplyRequest.Client):
    def apply_request(self, receiver, firstReceiver, action, handler):
        """
        Parameters:
         - receiver
         - firstReceiver
         - action

        """
        self.send_apply_request(receiver, firstReceiver, action)
        handler()
        return self.recv_apply_request()

class ApplyProcessor(Apply.Processor):

    def __init__(self, handler):
        super().__init__(handler)
        self.current_seqid = 0
        self.current_name = None
        self.handler = handler

    def process(self, iprot, oprot):
        (name, type, seqid) = iprot.readMessageBegin()
        self.current_seqid = seqid
        self.current_name = name
        if self._on_message_begin:
            self._on_message_begin(name, type, seqid)
        if name not in self._processMap:
            iprot.skip(TType.STRUCT)
            iprot.readMessageEnd()
            x = TApplicationException(TApplicationException.UNKNOWN_METHOD, 'Unknown function %s' % (name))
            oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
            x.write(oprot)
            oprot.writeMessageEnd()
            oprot.trans.flush()
            return
        else:
            self._processMap[name](self, seqid, iprot, oprot)
        if name == 'end_apply':
            return False
        return True

    def handle_exception(self, iprot, oprot, exc):
        x = TApplicationException(TApplicationException.INTERNAL_ERROR, exc)
        oprot.writeMessageBegin(self.current_name, TMessageType.EXCEPTION, self.current_seqid)
        x.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

class DebugChainTester(ChainTester):

    def __init__(self):
        super().__init__()
        self.debug_contracts = {}
        ipyeos_dir = os.path.dirname(__file__)
        self.so_file = None
        for f in os.listdir(ipyeos_dir):
            if f.endswith('.so'):
                self.so_file = os.path.join(ipyeos_dir, f)
        assert self.so_file

    def enable_debug_contract(self, contract, enable):
        self.debug_contracts[contract] = enable 
        if enable:
            eos.set_native_contract(contract, self.so_file)
        else:
            eos.set_native_contract(contract, "")

    def is_debug_contract_enabled(self, contract) -> bool:
        try:
            return self.debug_contracts[contract]
        except KeyError:
            return False

class ChainTesterHandler:
    def __init__(self, addr, vm_api_port, apply_request_addr, apply_request_port):
        self.testers: Dict[DebugChainTester] = {}
        self.tester_seq = 0
        _vm_api.set_apply_callback(self.on_apply)
        handler = VMAPIHandler()
        self.processor = ApplyProcessor(handler)
        transport = TSocket.TServerSocket(host=addr, port=vm_api_port)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()

        self.server = VMAPIServer(self.processor, transport, tfactory, pfactory)

        self.apply_request_transport = None
        self.apply_request_client = None

        self.current_tester: Optional[DebugChainTester] = None

        self.apply_request_addr = apply_request_addr
        self.apply_request_port = apply_request_port

    def get_apply_client(self):
        if not self.apply_request_client:
            self.apply_request_transport = TSocket.TSocket(self.apply_request_addr, self.apply_request_port)
            # Buffering is critical. Raw sockets are very slow
            self.apply_request_transport = TTransport.TBufferedTransport(self.apply_request_transport)
            # Wrap in a protocol
            protocol = TBinaryProtocol.TBinaryProtocol(self.apply_request_transport)
            # Create a client to use the protocol encoder
            self.apply_request_client = ApplyRequestClient(protocol)

            # Connect!
            for i in range(10):
                try:
                    self.apply_request_transport.open()
                    break
                except Exception as e:
                    time.sleep(0.001)
                    exc_info = sys.exc_info()
                    traceback.print_exception(*exc_info)
            else:
                raise Exception("connect to 9091 refused!")

        return self.apply_request_client

    def close_apply_client(self):
        if self.apply_request_client:
            self.apply_request_transport.close()
            self.apply_request_transport = None
            self.apply_request_client = None
        # self.server.close_vm_api_call_connection()

    def on_apply(self, receiver: u64, first_receiver: u64, action: u64):
        contract: str = eos.n2s(receiver)
        if not contract in self.current_tester.debug_contracts:
            return 0
        print('++++++on_apply:', eos.n2s(receiver), eos.n2s(first_receiver), eos.n2s(action))
        _a = to_uint64(receiver)
        _b = to_uint64(first_receiver)
        _c = to_uint64(action)
        ret = self.get_apply_client().apply_request(_a, _b, _c, self.vm_api_handler)
        return 1

    def vm_api_handler(self):
        self.server.handle_vm_api_call()

    def produce_block(self, id):
        self.testers[id].produce_block()

    def push_action(self, id: int, account: str, action: str, arguments: str, permissions: str):
        tester: DebugChainTester = self.testers[id]
        self.current_tester = tester
        # print('arguments:', arguments)
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            arguments = bytes.fromhex(arguments)

        permissions = json.loads(permissions)
        # print(account, action, arguments, permissions)
        # self.get_apply_client() # connect to apply request server
        try:
            r = tester.push_action(account, action, arguments, permissions)
            # r = tester.push_action(account, action, arguments, permissions, explicit_cpu_bill = True)
            return json.dumps(r).encode()
        except Exception as e:
            # logger.exception(e)
            err = e.args[0]
            if isinstance(err, dict):
                error_message = err['except']['stack']
                error_message = json.dumps(error_message)
                err = json.dumps(err)
            else:
                error_message = err
            self.server.handle_vm_api_exception(error_message)
            return err.encode()
        finally:
            self.current_tester = None
            self.get_apply_client().apply_end()

    def push_actions(self, id, actions):
        tester = self.testers[id]
        self.current_tester = tester
        _actions = []
        for a in actions:
            try:
                arguments = json.loads(a.arguments)
            except json.JSONDecodeError:
                arguments = bytes.fromhex(a.arguments)
            _actions.append([a.account, a.action, arguments, json.loads(a.permissions)])
        try:
            r = tester.push_actions(_actions)
            return json.dumps(r).encode()
        except Exception as e:
            err = e.args[0]
            if isinstance(err, dict):
                error_message = err['except']['stack']
                error_message = json.dumps(error_message)
                err = json.dumps(err)
            else:
                error_message = err
            self.server.handle_vm_api_exception(error_message)
            return err.encode()
        finally:
            self.current_tester = None
            self.get_apply_client().apply_end()

    def init_vm_api(self):
        self.server.init_vm_api_call()

    def init_apply_request(self):
        self.get_apply_client()

    def enable_debug_contract(self, id, contract, enable):
        self.testers[id].enable_debug_contract(contract, enable)

    def is_debug_contract_enabled(self, id, contract):
        self.testers[id].is_debug_contract_enabled(contract)

    def pack_abi(self, abi):
        return eos.pack_abi(abi)

    def pack_action_args(self, id, contract, action, action_args):
        action_args = json.loads(action_args)
        return self.testers[id].chain.pack_action_args(contract, action, action_args)

    def unpack_action_args(self, id, contract, action, raw_args):
        return self.testers[id].chain.unpack_action_args(contract, action, raw_args)

    def new_chain(self):
        self.tester_seq += 1
        tester = DebugChainTester()
        self.testers[self.tester_seq] = tester
        return self.tester_seq

    def free_chain(self, id):
        self.testers[id].free()
        del self.testers[id]
        # self.close_apply_client()
        # self.server.close_vm_api_call_connection()
        return 1

class VMAPIServer(TServer.TServer):
    """Simple single-threaded server that just pumps around one transport."""

    def __init__(self, *args):
        TServer.TServer.__init__(self, *args)
        self.serverTransport.listen()

        self.iprot = None
        self.oprot = None
        self.itrans = None
        self.otrans = None

        self.is_in_process_vm_api_call = False

    def close_vm_api_call_connection(self):
        if self.itrans:
            self.itrans.close()

        if self.otrans:
            self.otrans.close()

        self.iprot = None
        self.oprot = None
        self.itrans = None
        self.otrans = None

    def init_vm_api_call(self):
        if self.oprot:
            return
        client = self.serverTransport.accept()
        if not client:
            print('client is None')
            return
        print('new vm api client connection accepted!')
        self.itrans = self.inputTransportFactory.getTransport(client)
        self.iprot = self.inputProtocolFactory.getProtocol(self.itrans)

        # for THeaderProtocol, we must use the same protocol instance for
        # input and output so that the response is in the same dialect that
        # the server detected the request was in.
        if isinstance(self.inputProtocolFactory, THeaderProtocolFactory):
            self.otrans = None
            self.oprot = self.iprot
        else:
            self.otrans = self.outputTransportFactory.getTransport(client)
            self.oprot = self.outputProtocolFactory.getProtocol(self.otrans)

    def handle_vm_api_exception(self, exc):
        if self.is_in_process_vm_api_call:
            self.processor.handle_exception(self.iprot, self.oprot, exc)
        self.is_in_process_vm_api_call

    def handle_vm_api_call(self):
        self.init_vm_api_call()
        self.is_in_process_vm_api_call = True
        try:
            while self.processor.process(self.iprot, self.oprot):
                pass
        except TTransport.TTransportException as e:
            print('+++++++TTransport.TTransportException:', e)
            return
        except EndApplyException as e:
            return
            itrans.close()
            if otrans:
                otrans.close()
        except Exception as x:
            print('+++++++Exception:', x)
            # logger.exception(x)
            traceback.print_exc()
        finally:
            self.is_in_process_vm_api_call = False
        #     self.itrans.close()
        #     if self.otrans:
        #         self.otrans.close()

class ChainTesterServer(object):
    def __init__(self, *args, **kwargs):
        self.handler = kwargs['handler']
        if (len(args) == 2):
            self.__initArgs__(args[0], args[1],
                              TTransport.TTransportFactoryBase(),
                              TTransport.TTransportFactoryBase(),
                              TBinaryProtocol.TBinaryProtocolFactory(),
                              TBinaryProtocol.TBinaryProtocolFactory())
        elif (len(args) == 4):
            self.__initArgs__(args[0], args[1], args[2], args[2], args[3], args[3])
        elif (len(args) == 6):
            self.__initArgs__(args[0], args[1], args[2], args[3], args[4], args[5])

    def __initArgs__(self, processor, serverTransport,
                     inputTransportFactory, outputTransportFactory,
                     inputProtocolFactory, outputProtocolFactory):
        self.processor = processor
        self.serverTransport = serverTransport
        self.inputTransportFactory = inputTransportFactory
        self.outputTransportFactory = outputTransportFactory
        self.inputProtocolFactory = inputProtocolFactory
        self.outputProtocolFactory = outputProtocolFactory

        input_is_header = isinstance(self.inputProtocolFactory, THeaderProtocolFactory)
        output_is_header = isinstance(self.outputProtocolFactory, THeaderProtocolFactory)
        if any((input_is_header, output_is_header)) and input_is_header != output_is_header:
            raise ValueError("THeaderProtocol servers require that both the input and "
                             "output protocols are THeaderProtocol.")
    def serve(self):
        self.serverTransport.listen()
        while True:
            print('+++++++listening for new connection...')
            client = self.serverTransport.accept()
            if not client:
                continue

            itrans = self.inputTransportFactory.getTransport(client)
            iprot = self.inputProtocolFactory.getProtocol(itrans)

            # for THeaderProtocol, we must use the same protocol instance for
            # input and output so that the response is in the same dialect that
            # the server detected the request was in.
            if isinstance(self.inputProtocolFactory, THeaderProtocolFactory):
                otrans = None
                oprot = iprot
            else:
                otrans = self.outputTransportFactory.getTransport(client)
                oprot = self.outputProtocolFactory.getProtocol(otrans)

            try:
                while True:
                    self.processor.process(iprot, oprot)                    
            except TTransport.TTransportException:
                pass
            except Exception as x:
                logger.exception(x)

            print('+++++++client connection end')

            self.handler.close_apply_client()
            self.handler.server.close_vm_api_call_connection()

            itrans.close()
            if otrans:
                otrans.close()

def update_auth(chain, account):
    a = {
        "account": account,
        "permission": "active",
        "parent": "owner",
        "auth": {
            "threshold": 1,
            "keys": [
                {
                    "key": 'EOS6AjF6hvF7GSuSd4sCgfPKq5uWaXvGM2aQtEUCwmEHygQaqxBSV',
                    "weight": 1
                }
            ],
            "accounts": [{"permission":{"actor":account,"permission": 'eosio.code'}, "weight":1}],
            "waits": []
        }
    }
    chain.push_action('eosio', 'updateauth', a, {account:'active'})

class IPCChainTesterProcessor(IPCChainTester.Processor):
    def process(self, iprot, oprot):
        (name, type, seqid) = iprot.readMessageBegin()
        # print('IPCChainTesterProcessor:', name)
        if self._on_message_begin:
            self._on_message_begin(name, type, seqid)
        if name not in self._processMap:
            iprot.skip(TType.STRUCT)
            iprot.readMessageEnd()
            x = TApplicationException(TApplicationException.UNKNOWN_METHOD, 'Unknown function %s' % (name))
            oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
            x.write(oprot)
            oprot.writeMessageEnd()
            oprot.trans.flush()
            return
        else:
            self._processMap[name](self, seqid, iprot, oprot)
        if name == 'free_chain':
            return False
        return True

# result.addr, result.server_port, result.vm_api_port, result.apply_request_addr, result.apply_request_port
def start_debug_server(addr='127.0.0.1', server_port=9090, vm_api_port=9092, apply_request_addr='127.0.0.1', apply_request_port=9091):
    eos.enable_debug(True)
    eos.enable_native_contracts(True)
    handler = ChainTesterHandler(addr, vm_api_port, apply_request_addr, apply_request_port)
    processor = IPCChainTesterProcessor(handler)
    transport = TSocket.TServerSocket(host=addr, port=server_port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = ChainTesterServer(processor, transport, tfactory, pfactory, handler=handler)

    print('Starting the eos debugger server...')
    server.serve()
    print('done.')

if __name__ == '__main__':
    start_debug_server()
