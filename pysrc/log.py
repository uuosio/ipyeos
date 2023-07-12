import logging

log_format = '%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s %(lineno)d %(message)s'

class ColorFormatter(logging.Formatter):
    color_codes = {
        'DEBUG': '\033[32m',  # Green
        'INFO': '\033[0m',  # Reset
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[41m'  # Red background
    }

    def format(self, record):
        color_code = self.color_codes.get(record.levelname, '\033[0m')
        record.msg = f"{color_code}{record.msg}\033[0m"  # Reset color
        return super().format(record)


class ConnectionFormatter(logging.Formatter):
    color_codes = {
        'DEBUG': '\033[32m',  # Green
        'INFO': '\033[0m',  # Reset
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[41m'  # Red background
    }

    def __init__(self, conn):
        super().__init__(log_format)
        self.conn = conn

    def format(self, record):
        color_code = self.color_codes.get(record.levelname, '\033[0m')
        record.msg = f"{color_code}{self.conn.peer}: {record.msg}\033[0m"  # Reset color
        return super().format(record)

formater = ColorFormatter(log_format)
handler = logging.StreamHandler()
handler.setFormatter(formater)

# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s %(lineno)d %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S',
#                     handlers=[handler]
#                 )

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
