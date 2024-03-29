#
# Autogenerated by Thrift Compiler (0.15.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec

import sys
import logging
from .ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
all_structs = []


class Iface(object):
    def apply_request(self, receiver, firstReceiver, action, chainTesterId):
        """
        Parameters:
         - receiver
         - firstReceiver
         - action
         - chainTesterId

        """
        pass

    def apply_end(self, chainTesterId):
        """
        Parameters:
         - chainTesterId

        """
        pass


class Client(Iface):
    def __init__(self, iprot, oprot=None):
        self._iprot = self._oprot = iprot
        if oprot is not None:
            self._oprot = oprot
        self._seqid = 0

    def apply_request(self, receiver, firstReceiver, action, chainTesterId):
        """
        Parameters:
         - receiver
         - firstReceiver
         - action
         - chainTesterId

        """
        self.send_apply_request(receiver, firstReceiver, action, chainTesterId)
        return self.recv_apply_request()

    def send_apply_request(self, receiver, firstReceiver, action, chainTesterId):
        self._oprot.writeMessageBegin('apply_request', TMessageType.CALL, self._seqid)
        args = apply_request_args()
        args.receiver = receiver
        args.firstReceiver = firstReceiver
        args.action = action
        args.chainTesterId = chainTesterId
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_apply_request(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = apply_request_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.success is not None:
            return result.success
        raise TApplicationException(TApplicationException.MISSING_RESULT, "apply_request failed: unknown result")

    def apply_end(self, chainTesterId):
        """
        Parameters:
         - chainTesterId

        """
        self.send_apply_end(chainTesterId)
        return self.recv_apply_end()

    def send_apply_end(self, chainTesterId):
        self._oprot.writeMessageBegin('apply_end', TMessageType.CALL, self._seqid)
        args = apply_end_args()
        args.chainTesterId = chainTesterId
        args.write(self._oprot)
        self._oprot.writeMessageEnd()
        self._oprot.trans.flush()

    def recv_apply_end(self):
        iprot = self._iprot
        (fname, mtype, rseqid) = iprot.readMessageBegin()
        if mtype == TMessageType.EXCEPTION:
            x = TApplicationException()
            x.read(iprot)
            iprot.readMessageEnd()
            raise x
        result = apply_end_result()
        result.read(iprot)
        iprot.readMessageEnd()
        if result.success is not None:
            return result.success
        raise TApplicationException(TApplicationException.MISSING_RESULT, "apply_end failed: unknown result")


class Processor(Iface, TProcessor):
    def __init__(self, handler):
        self._handler = handler
        self._processMap = {}
        self._processMap["apply_request"] = Processor.process_apply_request
        self._processMap["apply_end"] = Processor.process_apply_end
        self._on_message_begin = None

    def on_message_begin(self, func):
        self._on_message_begin = func

    def process(self, iprot, oprot):
        (name, type, seqid) = iprot.readMessageBegin()
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
        return True

    def process_apply_request(self, seqid, iprot, oprot):
        args = apply_request_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = apply_request_result()
        try:
            result.success = self._handler.apply_request(args.receiver, args.firstReceiver, args.action, args.chainTesterId)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except TApplicationException as ex:
            logging.exception('TApplication exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = ex
        except Exception:
            logging.exception('Unexpected exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("apply_request", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

    def process_apply_end(self, seqid, iprot, oprot):
        args = apply_end_args()
        args.read(iprot)
        iprot.readMessageEnd()
        result = apply_end_result()
        try:
            result.success = self._handler.apply_end(args.chainTesterId)
            msg_type = TMessageType.REPLY
        except TTransport.TTransportException:
            raise
        except TApplicationException as ex:
            logging.exception('TApplication exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = ex
        except Exception:
            logging.exception('Unexpected exception in handler')
            msg_type = TMessageType.EXCEPTION
            result = TApplicationException(TApplicationException.INTERNAL_ERROR, 'Internal error')
        oprot.writeMessageBegin("apply_end", msg_type, seqid)
        result.write(oprot)
        oprot.writeMessageEnd()
        oprot.trans.flush()

# HELPER FUNCTIONS AND STRUCTURES


class apply_request_args(object):
    """
    Attributes:
     - receiver
     - firstReceiver
     - action
     - chainTesterId

    """


    def __init__(self, receiver=None, firstReceiver=None, action=None, chainTesterId=None,):
        self.receiver = receiver
        self.firstReceiver = firstReceiver
        self.action = action
        self.chainTesterId = chainTesterId

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRUCT:
                    self.receiver = Uint64()
                    self.receiver.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRUCT:
                    self.firstReceiver = Uint64()
                    self.firstReceiver.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.STRUCT:
                    self.action = Uint64()
                    self.action.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.I32:
                    self.chainTesterId = iprot.readI32()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('apply_request_args')
        if self.receiver is not None:
            oprot.writeFieldBegin('receiver', TType.STRUCT, 1)
            self.receiver.write(oprot)
            oprot.writeFieldEnd()
        if self.firstReceiver is not None:
            oprot.writeFieldBegin('firstReceiver', TType.STRUCT, 2)
            self.firstReceiver.write(oprot)
            oprot.writeFieldEnd()
        if self.action is not None:
            oprot.writeFieldBegin('action', TType.STRUCT, 3)
            self.action.write(oprot)
            oprot.writeFieldEnd()
        if self.chainTesterId is not None:
            oprot.writeFieldBegin('chainTesterId', TType.I32, 4)
            oprot.writeI32(self.chainTesterId)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(apply_request_args)
apply_request_args.thrift_spec = (
    None,  # 0
    (1, TType.STRUCT, 'receiver', [Uint64, None], None, ),  # 1
    (2, TType.STRUCT, 'firstReceiver', [Uint64, None], None, ),  # 2
    (3, TType.STRUCT, 'action', [Uint64, None], None, ),  # 3
    (4, TType.I32, 'chainTesterId', None, None, ),  # 4
)


class apply_request_result(object):
    """
    Attributes:
     - success

    """


    def __init__(self, success=None,):
        self.success = success

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 0:
                if ftype == TType.I32:
                    self.success = iprot.readI32()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('apply_request_result')
        if self.success is not None:
            oprot.writeFieldBegin('success', TType.I32, 0)
            oprot.writeI32(self.success)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(apply_request_result)
apply_request_result.thrift_spec = (
    (0, TType.I32, 'success', None, None, ),  # 0
)


class apply_end_args(object):
    """
    Attributes:
     - chainTesterId

    """


    def __init__(self, chainTesterId=None,):
        self.chainTesterId = chainTesterId

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.I32:
                    self.chainTesterId = iprot.readI32()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('apply_end_args')
        if self.chainTesterId is not None:
            oprot.writeFieldBegin('chainTesterId', TType.I32, 1)
            oprot.writeI32(self.chainTesterId)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(apply_end_args)
apply_end_args.thrift_spec = (
    None,  # 0
    (1, TType.I32, 'chainTesterId', None, None, ),  # 1
)


class apply_end_result(object):
    """
    Attributes:
     - success

    """


    def __init__(self, success=None,):
        self.success = success

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 0:
                if ftype == TType.I32:
                    self.success = iprot.readI32()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('apply_end_result')
        if self.success is not None:
            oprot.writeFieldBegin('success', TType.I32, 0)
            oprot.writeI32(self.success)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(apply_end_result)
apply_end_result.thrift_spec = (
    (0, TType.I32, 'success', None, None, ),  # 0
)
fix_spec(all_structs)
del all_structs
