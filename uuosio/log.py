import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s %(lineno)d %(message)s')

def get_logger(name):
    return logging.getLogger(name)
