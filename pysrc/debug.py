import inspect
import os
import socket

from . import log

logger = log.get_logger(__name__)

def get_caller_info():
    current_frame = inspect.currentframe()
    caller_frame = inspect.getouterframes(current_frame, 2)
    line_num = caller_frame[2][2]

    caller_frame = current_frame.f_back.f_back
    module_name = os.path.basename(inspect.getmodule(caller_frame).__name__)
    return module_name, line_num

def print_caller_info():
    current_frame = inspect.currentframe()
    caller_frame = inspect.getouterframes(current_frame, 2)
    line_num = caller_frame[2][2]

    caller_frame = current_frame.f_back.f_back
    module_name = os.path.basename(inspect.getmodule(caller_frame).__name__)
    logger.info(f"called from {module_name} at {line_num}:")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_free_port():
    port = 7777
    if 'DEBUG_PORT' in os.environ:
        return int(os.environ['DEBUG_PORT'])

    for i in range(10):
        port = 7777 + i
        if not is_port_in_use(port):
            return port

    raise Exception('can not find a free port')
