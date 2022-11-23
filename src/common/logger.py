import logging

class Logger:
    __logger: logging.Logger = logging.getLogger()

    @staticmethod
    def init():
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    @staticmethod
    def getLogger() -> logging.Logger:
        return Logger.__logger