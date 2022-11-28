import logging
import sys


class Logger(logging.Logger):
    logger = logging.getLogger("")

    @staticmethod
    def init(name = ""):
        if name != "":
            Logger.logger = logging.getLogger(name)
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    @staticmethod
    def info(msg, *args, **kwargs):
        Logger.logger.info(msg, *args, **kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        Logger.logger.error(msg, *args, **kwargs)

    @staticmethod
    def warning(msg, *args, **kwargs):
        Logger.logger.warning(msg, *args, **kwargs)

    @staticmethod
    def fatal(msg, *args, **kwargs):
        Logger.logger.fatal(msg, *args, **kwargs)
        sys.exit(1)

