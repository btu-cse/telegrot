import os

from peewee import MySQLDatabase

from src.common.utils.env_loader import load_env
from src.common.logger import Logger

load_env()


class DB:
    database = None

    def __init__(self):
        try:
            if DB.database == None:
                DB.database = MySQLDatabase(
                    database=os.getenv("MYSQL_DATABASE_NAME"),
                    host=os.getenv("MYSQL_DATABASE_HOST"),
                    user=os.getenv("MYSQL_DATABASE_USER"),
                    password=os.getenv("MYSQL_DATABASE_PASSWORD"),
                    port=int(os.getenv("MYSQL_DATABASE_PORT", 3306)),
                    charset="utf8",
                    ssl_key=os.getenv(
                        "CERTS_PRIVATE_KEY_FILE", 'certs/server.key'),
                    ssl_cert=os.getenv(
                        "CERTS_CERTIFICATE_FILE", 'certs/server.crt')
                )
        except Exception as e:
            Logger.error(
                "there is an error while connecting to the DB %s", e)

    @staticmethod
    def get_default_db():
        return DB.database
