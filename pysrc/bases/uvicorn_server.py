import uvicorn

from . import log

logger = log.get_logger(__name__)

class UvicornServer(uvicorn.Server):
    def install_signal_handlers(self):
        logger.info('install_signal_handlers ignored')

    def exit(self):
        self.should_exit = True
