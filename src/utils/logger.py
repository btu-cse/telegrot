import logging

class Logger:
    __logger: logging.Logger

    @staticmethod
    def init():
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        Logger.__logger = logging.getLogger()

    @staticmethod
    def getLogger() -> logging.Logger:
        return Logger.__logger