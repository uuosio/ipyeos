import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s %(lineno)d %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )

def get_logger(name):
    return logging.getLogger(name)
