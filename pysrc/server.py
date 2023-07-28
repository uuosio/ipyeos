import asyncio as aio
import glob
import json
import logging
import os
import queue
import string
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Dict, List, NewType, Optional

i32 = NewType('i32', int)
i64 = NewType('i64', int)
u64 = NewType('u64', int)

Iterator = NewType('Iterator', i32)

from thrift.protocol import TBinaryProtocol
from thrift.protocol.THeaderProtocol import THeaderProtocolFactory
from thrift.server import TServer
from thrift.Thrift import TApplicationException, TMessageType, TType
from thrift.transport import TSocket, TTransport

from . import _chainapi, _eos, _vm_api, chaintester, eos, log, rpc_server
from .chain_exceptions import ChainException, TransactionException
from .chainapi import ChainApi
from .chaintester import ChainTester
from .interfaces import Apply, ApplyRequest, IPCChainTester
from .interfaces.ttypes import (Action, ActionArguments, FindPrimaryReturn,
                                FindSecondaryReturn, GetResourceLimitsReturn,
                                LowerBoundUpperBoundReturn, NextPreviousReturn,
                                Uint64)

from .chain_exceptions import ChainException

chaintester.chain_config['contracts_console'] = True

logger = log.get_logger(__name__)
# logger.setLevel(logging.DEBUG)

thread_queue = queue.Queue()

def to_uint64(value):
    return Uint64(int.to_bytes(value, 8, 'little'))

def from_uint64(value):
    assert len(value.rawValue) == 8, 'bad Uint64'
    return int.from_bytes(value.rawValue, 'little')

def is_hex_string(s):
    return all(c in string.hexdigits for c in s)

class EndApplyException(Exception):
    pass

def check_cpp_exception(f):
    def wrapper(*args):
        ret = f(*args)
        if _vm_api.is_cpp_exception_occur():
            raise TApplicationException(TApplicationException.INTERNAL_ERROR, f"{f.__name__}: {args[1:]}")
        return ret
    return wrapper

class VMAPIHandler:
    def end_apply(self):
        return 1

    #chain.h
    # uint32_t get_active_producers( uint64_t* producers, uint32_t datalen );
    @check_cpp_exception
    def get_active_producers(self):
        return _vm_api.get_active_producers()

    #privileged.h
    # void get_resource_limits( uint64_t account, int64_t* ram_bytes, int64_t* net_weight, int64_t* cpu_weight );
    @check_cpp_exception
    def get_resource_limits(self, account: Uint64):
        ram_bytes, net_weight, cpu_weight = _vm_api.get_resource_limits(account.into())
        return GetResourceLimitsReturn(ram_bytes, net_weight, cpu_weight)

    # void set_resource_limits( uint64_t account, int64_t ram_bytes, int64_t net_weight, int64_t cpu_weight );
    @check_cpp_exception
    def set_resource_limits(self, account: Uint64, ram_bytes: i64, net_weight: i64, cpu_weight: i64):
        _vm_api.set_resource_limits(account.into(), ram_bytes, net_weight, cpu_weight)

    # int64_t set_proposed_producers( const char *producer_data, uint32_t producer_data_size );
    @check_cpp_exception
    def set_proposed_producers(self, producer_data: bytes):
        return _vm_api.set_proposed_producers(producer_data)

    # int64_t set_proposed_producers_ex( uint64_t producer_data_format, const char *producer_data, uint32_t producer_data_size );
    @check_cpp_exception
    def set_proposed_producers_ex(self, producer_data_format: Uint64, producer_data: bytes):
        return _vm_api.set_proposed_producers_ex(producer_data_format.into(), producer_data)

    # bool is_privileged( uint64_t account );
    @check_cpp_exception
    def is_privileged(self, account: Uint64):
        return _vm_api.is_privileged(account.into())

    # void set_privileged( uint64_t account, bool is_priv );
    @check_cpp_exception
    def set_privileged(self, account: Uint64, is_priv: bool):
        _vm_api.set_privileged(account.into(), is_priv)

    # void set_blockchain_parameters_packed( const char* data, uint32_t datalen );
    @check_cpp_exception
    def set_blockchain_parameters_packed(self, data: bytes):
        _vm_api.set_blockchain_parameters_packed(data)

    # uint32_t get_blockchain_parameters_packed( char* data, uint32_t datalen );
    @check_cpp_exception
    def get_blockchain_parameters_packed(self):
        return _vm_api.get_blockchain_parameters_packed()

    # void preactivate_feature( const capi_checksum256* feature_digest );
    @check_cpp_exception
    def preactivate_feature(self, feature_digest: bytes):
        return _vm_api.preactivate_feature(feature_digest)

    #permission.h
    # int32_t check_transaction_authorization( const char* trx_data, uint32_t trx_size,
    #                                 const char* pubkeys_data, uint32_t pubkeys_size,
    #                                 const char* perms_data,   uint32_t perms_size
    #                             );
    @check_cpp_exception
    def check_transaction_authorization(self, trx_data: bytes, pubkeys_data: bytes, perms_data: bytes):
        return _vm_api.check_transaction_authorization(trx_data, pubkeys_data, perms_data)

    # int32_t check_permission_authorization( uint64_t account,
    #                                 uint64_t permission,
    #                                 const char* pubkeys_data, uint32_t pubkeys_size,
    #                                 const char* perms_data,   uint32_t perms_size,
    #                                 uint64_t delay_us
    #                             );
    @check_cpp_exception
    def check_permission_authorization(self, account: Uint64, permission: Uint64, pubkeys_data: bytes, perms_data: bytes, delay_us: Uint64):
        return _vm_api.check_permission_authorization(account.into(), permission.into(), pubkeys_data, perms_data, delay_us.into())

    # int64_t get_permission_last_used( uint64_t account, uint64_t permission );
    @check_cpp_exception
    def get_permission_last_used(self, account: Uint64, permission: Uint64):
        return _vm_api.get_permission_last_used(account.into(), permission.into())

    # int64_t get_account_creation_time( uint64_t account );
    @check_cpp_exception
    def get_account_creation_time(self, account: Uint64):
        return _vm_api.get_account_creation_time(account.into())

    @check_cpp_exception
    def prints(self, msg):
        _vm_api.prints(msg)

#void prints_l( const char* cstr, uint32_t len);
    @check_cpp_exception
    def prints_l(self, cstr: bytes):
        _vm_api.prints_l(cstr)

    @check_cpp_exception
    def printi(self, n: i64):
        _vm_api.printi(n)

    @check_cpp_exception
    def printui(self, n: Uint64):
        _vm_api.printui(n.into())

    # void printi128( const int128_t* value );
    @check_cpp_exception
    def printi128(self, value: bytes):
        _vm_api.printi128(value)

    # void printui128( const uint128_t* value );
    @check_cpp_exception
    def printui128(self, value: bytes):
        _vm_api.printui128(value)

    # void printsf(float value);
    @check_cpp_exception
    def printsf(self, value: bytes):
        _vm_api.printsf(value)

    # void printdf(double value);
    @check_cpp_exception
    def printdf(self, value: bytes):
        _vm_api.printdf(value)

    # void printqf(const long double* value);
    @check_cpp_exception
    def printqf(self, value: bytes):
        _vm_api.printqf(value)

    # void printn( uint64_t name );
    @check_cpp_exception
    def printn(self, name: Uint64):
        _vm_api.printn(name.into())

    # void printhex( const void* data, uint32_t datalen );
    @check_cpp_exception
    def printhex(self, data: bytes):
        _vm_api.printhex(data)

    @check_cpp_exception
    def action_data_size(self):
        return _vm_api.action_data_size()

    @check_cpp_exception
    def read_action_data(self):
        return _vm_api.read_action_data()

    # void require_recipient( uint64_t name );
    @check_cpp_exception
    def require_recipient(self, name: Uint64):
        _vm_api.require_recipient(name.into())

    # void require_auth( uint64_t name );
    @check_cpp_exception
    def require_auth(self, name: Uint64):
        _vm_api.require_auth(name.into())

    # bool has_auth( uint64_t name );
    @check_cpp_exception
    def has_auth(self, name: Uint64):
        return _vm_api.has_auth(name.into())

    # void require_auth2( uint64_t name, uint64_t permission );
    @check_cpp_exception
    def require_auth2(self, name: Uint64, permission: Uint64):
        _vm_api.require_auth2(name.into(), permission.into())

    # bool is_account( uint64_t name );
    @check_cpp_exception
    def is_account(self, name: Uint64):
        return _vm_api.is_account(name.into())

    @check_cpp_exception
    def send_inline(self, serialized_data):
        _vm_api.send_inline(serialized_data)

    @check_cpp_exception
    def send_context_free_inline(self, serialized_data: bytes):
        _vm_api.send_context_free_inline(serialized_data)

    # uint64_t  publication_time();
    @check_cpp_exception
    def publication_time(self):
        ret = _vm_api.publication_time()
        return to_uint64(ret)

    # uint64_t current_receiver();
    @check_cpp_exception
    def current_receiver(self, ):
        ret = _vm_api.current_receiver()
        return to_uint64(ret)

    # void  eosio_assert( uint32_t test, const char* msg );
    @check_cpp_exception
    @check_cpp_exception
    def eosio_assert(self, test, msg: bytes):
        _vm_api.eosio_assert(test, msg)

    # void  eosio_assert_message( uint32_t test, const char* msg, uint32_t msg_len );
    @check_cpp_exception
    def eosio_assert_message(self, test, msg: bytes):
        _vm_api.eosio_assert_message(test, msg)

    # void  eosio_assert_code( uint32_t test, uint64_t code );
    @check_cpp_exception
    def eosio_assert_code(self, test, code):
        _vm_api.eosio_assert_code(test, code.into())

    # void eosio_exit( int32_t code );
    @check_cpp_exception
    def eosio_exit(self, code: i32):
        _vm_api.eosio_exit(code)

    # uint64_t  current_time();
    @check_cpp_exception
    def current_time(self):
        ret = _vm_api.current_time()
        return to_uint64(ret)

    # bool is_feature_activated( const capi_checksum256* feature_digest );
    @check_cpp_exception
    def is_feature_activated(self, feature_digest: bytes):
        return _vm_api.is_feature_activated(feature_digest)

    # uint64_t get_sender();
    @check_cpp_exception
    def get_sender(self):
        ret = _vm_api.get_sender()
        return to_uint64(ret)

    # void assert_sha256( const char* data, uint32_t length, const capi_checksum256* hash );
    @check_cpp_exception
    def assert_sha256(self, data: bytes, hash: bytes):
        _vm_api.assert_sha256(data, hash)

    # void assert_sha1( const char* data, uint32_t length, const capi_checksum160* hash );
    @check_cpp_exception
    def assert_sha1(self, data: bytes, hash: bytes):
        _vm_api.assert_sha1(data, hash)

    # void assert_sha512( const char* data, uint32_t length, const capi_checksum512* hash );
    @check_cpp_exception
    def assert_sha512(self, data: bytes, hash: bytes):
        _vm_api.assert_sha512(data, hash)

    # void assert_ripemd160( const char* data, uint32_t length, const capi_checksum160* hash );
    @check_cpp_exception
    def assert_ripemd160(self, data: bytes, hash: bytes):
        _vm_api.assert_ripemd160(data, hash)

    # void sha256( const char* data, uint32_t length, capi_checksum256* hash );
    @check_cpp_exception
    def sha256(self, data: bytes):
        return _vm_api.sha256(data)

    # void sha1( const char* data, uint32_t length, capi_checksum160* hash );
    @check_cpp_exception
    def sha1(self, data: bytes):
        return _vm_api.sha1(data)

    # void sha512( const char* data, uint32_t length, capi_checksum512* hash );
    @check_cpp_exception
    def sha512(self, data: bytes):
        return _vm_api.sha512(data)

    # void ripemd160( const char* data, uint32_t length, capi_checksum160* hash );
    @check_cpp_exception
    def ripemd160(self, data: bytes):
        return _vm_api.ripemd160(data)

    # int32_t recover_key( const capi_checksum256* digest, const char* sig, uint32_t siglen, char* pub, uint32_t publen );
    @check_cpp_exception
    def recover_key(self, digest: bytes, sig: bytes):
        return _vm_api.recover_key(digest, sig)

    # void assert_recover_key( const capi_checksum256* digest, const char* sig, uint32_t siglen, const char* pub, uint32_t publen );
    @check_cpp_exception
    def assert_recover_key(self, digest: bytes, sig: bytes, pub: bytes):
        _vm_api.assert_recover_key(digest, sig, pub)


    #transaction.h
    # void send_deferred(const uint128_t sender_id, uint64_t payer, const char *serialized_transaction, uint32_t size, uint32_t replace_existing = 0);
    @check_cpp_exception
    def send_deferred(self, sender_id: bytes, payer: Uint64, serialized_transaction: bytes, replace_existing: i32):
        _vm_api.send_deferred(sender_id, payer.into(), serialized_transaction, replace_existing)

    # int32_t cancel_deferred(const uint128_t sender_id);
    @check_cpp_exception
    def cancel_deferred(self, sender_id: bytes):
        return _vm_api.cancel_deferred(sender_id)

    # uint32_t read_transaction(char *buffer, uint32_t size);
    @check_cpp_exception
    def read_transaction(self):
        return _vm_api.read_transaction()

    # uint32_t transaction_size();
    @check_cpp_exception
    def transaction_size(self):
        return _vm_api.transaction_size()

    # int32_t tapos_block_num();
    @check_cpp_exception
    def tapos_block_num(self):
        return _vm_api.tapos_block_num()

    # int32_t tapos_block_prefix();
    @check_cpp_exception
    def tapos_block_prefix(self):
        return _vm_api.tapos_block_prefix()

    # uint32_t expiration();
    @check_cpp_exception
    def expiration(self):
        return _vm_api.expiration()

    # int32_t get_action( uint32_t type, uint32_t index, char* buff, uint32_t size );
    @check_cpp_exception
    def get_action(self, _type: i32, index: i32):
        return _vm_api.get_action(_type, index)

    # int32_t get_context_free_data( uint32_t index, char* buff, uint32_t size );
    @check_cpp_exception
    def get_context_free_data(self, index: i32):
        return _vm_api.get_action(index)

    @check_cpp_exception
    def set_action_return_value(self, data: bytes):
        _vm_api.set_action_return_value(data)

    @check_cpp_exception
    def get_code_hash(self, account, struct_version):
        return _vm_api.get_code_hash(account.into(), struct_version)

    @check_cpp_exception
    def get_block_num(self):
        return _vm_api.get_block_num()

    @check_cpp_exception
    def sha3(self, data, keccak):
        return _vm_api.sha3(data, keccak)

    @check_cpp_exception
    def blake2_f(self, rounds, state, msg, t0_offset, t1_offset, final):
        return _vm_api.blake2_f(rounds, state, msg, t0_offset, t1_offset, final)

    @check_cpp_exception
    def k1_recover(self, sig, dig):
        return _vm_api.k1_recover(sig, dig)

    @check_cpp_exception
    def alt_bn128_add(self, op1, op2):
        return _vm_api.alt_bn128_add(op1, op2)

    @check_cpp_exception
    def alt_bn128_mul(self, g1, scalar):
        return _vm_api.alt_bn128_mul(g1, scalar)

    @check_cpp_exception
    def alt_bn128_pair(self, pairs):
        return _vm_api.alt_bn128_pair(pairs)

    @check_cpp_exception
    def mod_exp(self, base, exp, mod):
        return _vm_api.mod_exp(base, exp, mod)

    @check_cpp_exception
    def db_store_i64(self, scope: Uint64, table: Uint64, payer: Uint64, id: Uint64, data: bytes):
        return _vm_api.db_store_i64(scope.into(), table.into(), payer.into(), id.into(), data)

    @check_cpp_exception
    def db_update_i64(self, iterator: i32, payer: Uint64, data: bytes):
        return _vm_api.db_update_i64(iterator, payer.into(), data)

    @check_cpp_exception
    def db_remove_i64(self, iterator: i32):
        return _vm_api.db_remove_i64(iterator)

    @check_cpp_exception
    def db_get_i64(self, iterator: i32):
        return _vm_api.db_get_i64(iterator)

    @check_cpp_exception
    def db_next_i64(self, iterator: i32):
        it, primary = _vm_api.db_next_i64(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_previous_i64(self, iterator: i32):
        it, primary = _vm_api.db_previous_i64(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_find_i64(self, code: Uint64, scope: Uint64, table: Uint64, id: Uint64):
        return _vm_api.db_find_i64(code.into(), scope.into(), table.into(), id.into())

    @check_cpp_exception
    def db_lowerbound_i64(self, code: Uint64, scope: Uint64, table: Uint64, id: Uint64):
        return _vm_api.db_lowerbound_i64(code.into(), scope.into(), table.into(), id.into())

    @check_cpp_exception
    def db_upperbound_i64(self, code: Uint64, scope: Uint64, table: Uint64, id: Uint64):
        return _vm_api.db_upperbound_i64(code.into(), scope.into(), table.into(), id.into())

    @check_cpp_exception
    def db_end_i64(self, code: Uint64, scope: Uint64, table: Uint64):
        return _vm_api.db_end_i64(code.into(), scope.into(), table.into())

    @check_cpp_exception
    def db_idx64_store(self, scope: Uint64, table: Uint64, payer: Uint64, id: Uint64, secondary: Uint64) -> i32:
        return _vm_api.db_idx64_store(scope.into(), table.into(), payer.into(), id.into(), secondary.into())

    @check_cpp_exception
    def db_idx64_update(self, iterator: i32, payer: Uint64, secondary: Uint64):
        _vm_api.db_idx64_update(iterator, payer.into(), secondary.into())

    @check_cpp_exception
    def db_idx64_remove(self, iterator: i32) -> i32:
        _vm_api.db_idx64_remove(iterator)

    @check_cpp_exception
    def db_idx64_next(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx64_next(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx64_previous(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx64_previous(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx64_find_primary(self, code: Uint64, scope: Uint64, table: Uint64, primary: Uint64) -> FindPrimaryReturn:
        it, secondary = _vm_api.db_idx64_find_primary(code.into(), scope.into(), table.into(), primary.into())
        return FindPrimaryReturn(it, secondary)

    @check_cpp_exception
    def db_idx64_find_secondary(self, code: Uint64, scope: Uint64, table: Uint64, secondary: Uint64) -> FindSecondaryReturn:
        it, primary = _vm_api.db_idx64_find_secondary(code.into(), scope.into(), table.into(), secondary.into())
        return FindSecondaryReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx64_lowerbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary: Uint64, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx64_lowerbound(code.into(), scope.into(), table.into(), secondary.into(), primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    @check_cpp_exception
    def db_idx64_upperbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary, primary):
        it, secondary, primary = _vm_api.db_idx64_upperbound(code.into(), scope.into(), table.into(), secondary.into(), primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    @check_cpp_exception
    def db_idx64_end(self, code: Uint64, scope: Uint64, table: Uint64):
        return _vm_api.db_idx64_end(code.into(), scope.into(), table.into())

    @check_cpp_exception
    def db_idx128_store(self, scope: Uint64, table: Uint64, payer: Uint64, id, secondary: bytes):
        return _vm_api.db_idx128_store(scope.into(), table.into(), payer.into(), id.into(), secondary)

    @check_cpp_exception
    def db_idx128_update(self, iterator: i32, payer: Uint64, secondary: bytes):
        return _vm_api.db_idx128_update(iterator, payer.into(), secondary)

    @check_cpp_exception
    def db_idx128_remove(self, iterator: i32):
        _vm_api.db_idx128_remove(iterator)

    @check_cpp_exception
    def db_idx128_next(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx128_next(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx128_previous(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx128_previous(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx128_find_primary(self, code: Uint64, scope: Uint64, table: Uint64, primary: Uint64):
        it, secondary = _vm_api.db_idx128_find_primary(code.into(), scope.into(), table.into(), primary.into())
        return FindPrimaryReturn(it, secondary)

    @check_cpp_exception
    def db_idx128_find_secondary(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes) -> FindSecondaryReturn:
        it, primary = _vm_api.db_idx128_find_secondary(code.into(), scope.into(), table.into(), secondary)
        return FindSecondaryReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx128_lowerbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx128_lowerbound(code.into(), scope.into(), table.into(), secondary, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    @check_cpp_exception
    def db_idx128_upperbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx128_upperbound(code.into(), scope.into(), table.into(), secondary, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    @check_cpp_exception
    def db_idx128_end(self, code: Uint64, scope: Uint64, table: Uint64):
        return _vm_api.db_idx128_end(code.into(), scope.into(), table.into())

    @check_cpp_exception
    def db_idx256_store(self, scope: Uint64, table: Uint64, payer: Uint64, id: Uint64, data: bytes) -> i32:
        return _vm_api.db_idx256_store(scope.into(), table.into(), payer.into(), id.into(), data)

    @check_cpp_exception
    def db_idx256_update(self, iterator: i32, payer: Uint64, data: bytes):
        return _vm_api.db_idx256_update(iterator, payer.into(), data)

    @check_cpp_exception
    def db_idx256_remove(self, iterator: i32):
        _vm_api.db_idx256_remove(iterator)

    @check_cpp_exception
    def db_idx256_next(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx256_next(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx256_previous(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx256_previous(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx256_find_primary(self, code: Uint64, scope: Uint64, table: Uint64, primary: Uint64):
        it, secondary = _vm_api.db_idx256_find_primary(code.into(), scope.into(), table.into(), primary.into())
        return FindPrimaryReturn(it, secondary)

    @check_cpp_exception
    def db_idx256_find_secondary(self, code: Uint64, scope: Uint64, table: Uint64, data: bytes) -> FindSecondaryReturn:
        it, primary = _vm_api.db_idx256_find_secondary(code.into(), scope.into(), table.into(), data)
        return FindSecondaryReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx256_lowerbound(self, code: Uint64, scope: Uint64, table: Uint64, data: bytes, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx256_lowerbound(code.into(), scope.into(), table.into(), data, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    @check_cpp_exception
    def db_idx256_upperbound(self, code: Uint64, scope: Uint64, table: Uint64, data, primary):
        it, secondary, primary = _vm_api.db_idx256_upperbound(code.into(), scope.into(), table.into(), data, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    @check_cpp_exception
    def db_idx256_end(self, code: Uint64, scope: Uint64, table: Uint64):
        return _vm_api.db_idx256_end(code.into(), scope.into(), table.into())

    @check_cpp_exception
    def db_idx_double_store(self, scope: Uint64, table: Uint64, payer: Uint64, id: Uint64, secondary: bytes):
        return _vm_api.db_idx_double_store(scope.into(), table.into(), payer.into(), id.into(), secondary)

    @check_cpp_exception
    def db_idx_double_update(self, iterator: i32, payer: Uint64, secondary: bytes):
        return _vm_api.db_idx_double_update(iterator, payer.into(), secondary)

    @check_cpp_exception
    def db_idx_double_remove(self, iterator: i32):
        _vm_api.db_idx_double_remove(iterator)

    @check_cpp_exception
    def db_idx_double_next(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx_double_next(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx_double_previous(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx_double_previous(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx_double_find_primary(self, code: Uint64, scope: Uint64, table: Uint64, primary: Uint64):
        it, secondary = _vm_api.db_idx_double_find_primary(code.into(), scope.into(), table.into(), primary.into())
        return FindPrimaryReturn(it, secondary)

    @check_cpp_exception
    def db_idx_double_find_secondary(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes) -> FindSecondaryReturn:
        it, primary = _vm_api.db_idx_double_find_secondary(code.into(), scope.into(), table.into(), secondary)
        return FindSecondaryReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx_double_lowerbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx_double_lowerbound(code.into(), scope.into(), table.into(), secondary, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    @check_cpp_exception
    def db_idx_double_upperbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx_double_upperbound(code.into(), scope.into(), table.into(), secondary, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    @check_cpp_exception
    def db_idx_double_end(self, code: Uint64, scope: Uint64, table: Uint64):
        return _vm_api.db_idx_double_end(code.into(), scope.into(), table.into())

    @check_cpp_exception
    def db_idx_long_double_store(self, scope: Uint64, table: Uint64, payer: Uint64, id: Uint64, secondary: bytes):
        return _vm_api.db_idx_long_double_store(scope.into(), table.into(), payer.into(), id.into(), secondary)

    @check_cpp_exception
    def db_idx_long_double_update(self, iterator: i32, payer: Uint64, secondary: bytes):
        return _vm_api.db_idx_long_double_update(iterator, payer.into(), secondary)

    @check_cpp_exception
    def db_idx_long_double_remove(self, iterator: i32):
        _vm_api.db_idx_long_double_remove(iterator)

    @check_cpp_exception
    def db_idx_long_double_next(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx_long_double_next(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx_long_double_previous(self, iterator: i32) -> NextPreviousReturn:
        it, primary = _vm_api.db_idx_long_double_previous(iterator)
        return NextPreviousReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx_long_double_find_primary(self, code: Uint64, scope: Uint64, table: Uint64, primary: Uint64):
        it, secondary = _vm_api.db_idx_long_double_find_primary(code.into(), scope.into(), table.into(), primary.into())
        return FindPrimaryReturn(it, secondary)

    @check_cpp_exception
    def db_idx_long_double_find_secondary(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes) -> FindSecondaryReturn:
        it, primary = _vm_api.db_idx_long_double_find_secondary(code.into(), scope.into(), table.into(), secondary)
        return FindSecondaryReturn(it, to_uint64(primary))

    @check_cpp_exception
    def db_idx_long_double_lowerbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx_long_double_lowerbound(code.into(), scope.into(), table.into(), secondary, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    @check_cpp_exception
    def db_idx_long_double_upperbound(self, code: Uint64, scope: Uint64, table: Uint64, secondary: bytes, primary: Uint64):
        it, secondary, primary = _vm_api.db_idx_long_double_upperbound(code.into(), scope.into(), table.into(), secondary, primary.into())
        return LowerBoundUpperBoundReturn(it, secondary, to_uint64(primary))

    @check_cpp_exception
    def db_idx_long_double_end(self, code: Uint64, scope: Uint64, table: Uint64):
        return _vm_api.db_idx_long_double_end(code.into(), scope.into(), table.into())

class ApplyRequestClient(ApplyRequest.Client):
    def apply_request(self, receiver, firstReceiver, action, handler, chain_tester_id):
        """
        Parameters:
         - receiver
         - firstReceiver
         - action

        """
        self.send_apply_request(receiver, firstReceiver, action, chain_tester_id)
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

    def __init__(self, id: int, initialize: bool):
        super().__init__(initialize)
        self.id = id
        self.debug_contracts = {}
        ipyeos_dir = os.path.dirname(__file__)
        self.so_file = None
        for f in os.listdir(ipyeos_dir):
            if f.endswith('.so'):
                self.so_file = os.path.join(ipyeos_dir, f)
                break
        assert self.so_file

    def enable_debug_contract(self, contract: str, enable: bool):
        self.debug_contracts[contract] = enable 
        if enable:
            eos.enable_debug(True)
            self.chain.set_native_contract(contract, self.so_file)
        else:
            self.chain.set_native_contract(contract, "")

    def is_debug_contract_enabled(self, contract) -> bool:
        try:
            return self.debug_contracts[contract]
        except KeyError:
            return False

class CurrentConnection(object):
    def __init__(self, addr):
        self.addr = addr
        self.chain_seq_nums = set()

    def add_chain_seq_num(self, seq_num):
        self.chain_seq_nums.add(seq_num)

    def get_chain_seq_nums(self):
        return self.chain_seq_nums

    def remove_chain_seq_num(self, seq_num):
        if seq_num in self.chain_seq_nums:
            self.chain_seq_nums.remove(seq_num)

class ChainTesterHandler:
    def __init__(self, addr, vm_api_port, apply_request_addr, apply_request_port):
        self.testers: dict[DebugChainTester] = {}
        self.tester_seq = 1
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

        self.current_connection: CurrentConnection = None

    def on_close_client(self):
        for seq_num in list(self.current_connection.get_chain_seq_nums()):
            self.free_chain(seq_num)
        self.current_connection = None
        self.close_apply_client()
        self.server.close_vm_api_call_connection()

    def set_current_connection(self, addr):
        self.current_connection = CurrentConnection(addr)

    def init_apply_request_client(self):
        if not self.apply_request_client:
            self.apply_request_transport = TSocket.TSocket(self.apply_request_addr, self.apply_request_port)
            self.apply_request_transport = TTransport.TBufferedTransport(self.apply_request_transport)
            protocol = TBinaryProtocol.TBinaryProtocol(self.apply_request_transport)
            self.apply_request_client = ApplyRequestClient(protocol)

            time.sleep(0.1)
            # Connect!
            for i in range(10):
                try:
                    self.apply_request_transport.open()
                    print('connected to apply request server!')
                    break
                except Exception as e:
                    exc_info = sys.exc_info()
                    traceback.print_exception(*exc_info)
                    time.sleep(0.1)
            else:
                raise Exception("connect to 9091 refused!")

    def get_apply_request_client(self):
        return self.apply_request_client

    def close_apply_client(self):
        if self.apply_request_client:
            self.apply_request_transport.close()
            self.apply_request_transport = None
            self.apply_request_client = None
        # self.server.close_vm_api_call_connection()

    def on_apply(self, receiver: u64, first_receiver: u64, action: u64):
        print('++++++on_apply:', eos.n2s(receiver), eos.n2s(first_receiver), eos.n2s(action))
        contract: str = eos.n2s(receiver)
        if not self.current_tester:
            return 0
        if not contract in self.current_tester.debug_contracts:
            return 0
        _a = to_uint64(receiver)
        _b = to_uint64(first_receiver)
        _c = to_uint64(action)
        ret = self.get_apply_request_client().apply_request(_a, _b, _c, self.vm_api_handler, self.current_tester.id)
        return 1

    def vm_api_handler(self):
        self.server.handle_vm_api_call()

    def produce_block(self, id, next_block_skip_seconds: int = 0):
        tester: ChainTester = self.testers[id]
        self.current_tester = tester
        if next_block_skip_seconds == 0:
            tester.produce_block()
        else:
            pending_block_time = tester.chain.pending_block_time() // 1000
            next_block_time = pending_block_time + next_block_skip_seconds * 1000
            tester.produce_block(next_block_time)

        self.current_tester = None
        client = self.get_apply_request_client()
        if client:
            client.apply_end(tester.id)

    def push_action(self, id: int, account: str, action: str, arguments: ActionArguments, permissions: str):
        tester: DebugChainTester = self.testers[id]
        self.current_tester = tester
        # print('++++++++++++arguments:', arguments)
        if not arguments.raw_args is None:
            arguments = arguments.raw_args
        else:
            arguments = arguments.json_args
        try:
            permissions = json.loads(permissions)
            r = tester.push_action(account, action, arguments, permissions)
            # r = tester.push_action(account, action, arguments, permissions, explicit_cpu_bill = True)
            return json.dumps(r).encode()
        except TransactionException as e:
            logger.exception(e)
            return str(e).encode()
        except ChainException as e:
            logger.exception(e)
            return str(e).encode()
        except Exception as e:
            logger.exception(e)
            return str(e).encode()
        finally:
            self.current_tester = None
            client = self.get_apply_request_client()
            if client:
                client.apply_end(tester.id)

    def push_actions(self, id, actions: List[Action]):
        tester = self.testers[id]
        self.current_tester = tester
        _actions = []
        for a in actions:
            arguments = a.arguments
            permissions = a.permissions
            try:
                if not arguments.raw_args is None:
                    arguments = arguments.raw_args
                else:
                    arguments = arguments.json_args
                permissions = json.loads(permissions)
            except json.JSONDecodeError as e:
                err = {
                    'except': str(e)
                }
                client = self.get_apply_request_client()
                if client:
                    client.apply_end(tester.id)
                return json.dumps(err).encode()
            _actions.append([a.account, a.action, arguments, permissions])
        try:
            r = tester.push_actions(_actions)
            return json.dumps(r).encode()
        except ChainException as e:
            logger.exception(e)
            return str(e).encode()
        except TransactionException as e:
            logger.exception(e)
            return str(e).encode()
        except Exception as e:
            logger.exception(e)
            err = e.args[0]
            if isinstance(err, dict):
                error_message = err['except']
                error_message = json.dumps(error_message)
                err = json.dumps(err)
            else:
                error_message = err
            self.server.handle_vm_api_exception(error_message)
            return err.encode()
        finally:
            self.current_tester = None
            client = self.get_apply_request_client()
            if client:
                client.apply_end(tester.id)

    def deploy_contract(self, id, account: str, wasm: str, abi: str):
        tester: ChainTester = self.testers[id]
        try:
            ret = tester.deploy_contract(account, bytes.fromhex(wasm), abi)
            return json.dumps(ret).encode()
        except Exception as e:
            logger.exception(e)
            err = e.args[0]
            if isinstance(err, dict):
                err = json.dumps(err)
            return err.encode()

    def create_account(self, id: int, creator: str, account: str, owner_key: str, active_key: str, ram_bytes: int=0, stake_net: i64=0, stake_cpu: i64=0):
        tester: ChainTester = self.testers[id]
        ret = tester.create_account(creator, account, owner_key, active_key, ram_bytes, stake_net, stake_cpu)
        return json.dumps(ret)

    def create_key(self, key_type):
        return _eos.create_key(key_type)

    def get_table_rows(self, id, _json: bool, code: str, scope: str, table: str, lower_bound: str, upper_bound: str, limit: i64, key_type: str, index_position: str, encode_type: str, reverse: bool, show_payer: bool):
        tester: ChainTester = self.testers[id]
        # print(_json, code, scope, table, lower_bound, upper_bound, limit, key_type, index_position, reverse, show_payer)
        try:
            r = tester.get_table_rows(_json, code, scope, table, lower_bound, upper_bound, limit, key_type, index_position, encode_type, reverse, show_payer)
            return json.dumps(r)
        except Exception as e:
            print(e)
            return str(e)

    def init_vm_api(self):
        self.server.init_vm_api_call()

    def init_apply_request(self):
        self.init_apply_request_client()

    def enable_debugging(self, enable: bool):
        eos.enable_debug(enable)

    def set_native_contract(self, id: int, contract: str, dylib: str):
        """Loading a shared library for debugging

        Args:
            contract (str): contract for debugging
            dylib (str): shared library path
        """
        tester: ChainTester = self.testers[id]
        return tester.chain.set_native_contract(contract, dylib)
    def enable_debug_contract(self, id, contract, enable):
        self.testers[id].enable_debug_contract(contract, enable)

    def is_debug_contract_enabled(self, id, contract):
        self.testers[id].is_debug_contract_enabled(contract)

    def pack_abi(self, abi):
        return eos.pack_abi(abi)

    def pack_action_args(self, id, contract, action, action_args):
        action_args = json.loads(action_args)
        return self.testers[id].pack_action_args(contract, action, action_args)

    def unpack_action_args(self, id, contract, action, raw_args):
        return self.testers[id].chain.unpack_action_args(contract, action, raw_args)

    def new_chain(self, initialize: bool=True):
        # max 100 test chain per connection
        if self.current_connection and len(self.current_connection.get_chain_seq_nums()) >= 100:
            return 0
        self.tester_seq += 1
        tester = DebugChainTester(self.tester_seq, initialize)
        self.testers[self.tester_seq] = tester
        if self.current_connection:
            self.current_connection.add_chain_seq_num(self.tester_seq)
        return self.tester_seq

    def free_chain(self, id):
        if self.current_connection:
            self.current_connection.remove_chain_seq_num(id)
        if id in self.testers:
            self.testers[id].free()
            del self.testers[id]
        # self.close_apply_client()
        # self.server.close_vm_api_call_connection()
            return 1
        else:
            return 0

    def get_info(self, id: i32):
        chain = self.testers[id].chain
        success, ret = _chainapi.get_info(chain.ptr)
        if not success:
            return chain.get_last_error()
        return ret

    def get_account(self, id: i32, account: str):
        chain = self.testers[id].chain
        args = {'account_name': account}
        args = json.dumps(args)
        success, ret = _chainapi.get_account(chain.ptr, args)
        if not success:
            return chain.get_last_error()
        return ret

    def import_key(self, id: i32, pub_key: str, priv_key: str):
        chain: ChainTester = self.testers[id]
        return chain.import_key(priv_key)

    def get_required_keys(self, id: i32, transaction: str, available_keys: List[str]):
        chain = self.testers[id].chain
        params = dict(
            transaction = json.loads(transaction),
            available_keys = available_keys,
        )
        params = json.dumps(params)
        success, ret = _chainapi.get_required_keys(chain.ptr, params)
        if not success:
            return chain.get_last_error()
        return ret

    def quit(self):
        thread_queue.put('exit')
        return True

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
        self.handler: ChainTesterHandler = kwargs['handler']
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
        self.serverTransport: TSocket.TServerSocket = serverTransport
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
            print('Listening for new connection...')
            client = self.serverTransport.accept()
            if not client:
                continue
            try:
                self.handler.set_current_connection('%s:%d'%client.handle.getpeername())
                itrans = self.inputTransportFactory.getTransport(client)
                iprot = self.inputProtocolFactory.getProtocol(itrans)
            except Exception as e:
                logger.exception(e)
                continue

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

            self.handler.on_close_client()

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
        (name, _type, seqid) = iprot.readMessageBegin()
        # print('IPCChainTesterProcessor:', name)
        if self._on_message_begin:
            self._on_message_begin(name, _type, seqid)
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
def start_debug_server(addr='127.0.0.1', server_port=9090, vm_api_port=9092, apply_request_addr='127.0.0.1', apply_request_port=9091, rpc_server_addr='127.0.0.1', rpc_server_port=9093):
    eos.enable_debug(True)
    handler = ChainTesterHandler(addr, vm_api_port, apply_request_addr, apply_request_port)
    processor = IPCChainTesterProcessor(handler)

    def start_server():
        print('Starting the EOS debugger server...')
        transport = TSocket.TServerSocket(host=addr, port=server_port)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()

        server = ChainTesterServer(processor, transport, tfactory, pfactory, handler=handler)
        server.serve()
        print('done.')

    def start_rpc_server():
        loop = aio.new_event_loop()
        try:
            loop.run_until_complete(rpc_server.start(rpc_server_addr, rpc_server_port, handler))
        except KeyboardInterrupt:
            loop.stop()
            loop.close()

    t = threading.Thread(target=start_rpc_server, daemon=True)
    t.start()

    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    while True:
        try:
            command = thread_queue.get(block=True)
            if command == 'exit':
                time.sleep(1.0)
                sys.exit(0)
                break
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")
            sys.exit(0)

if __name__ == '__main__':
    start_debug_server()

