import os

from peewee import MySQLDatabase

from src.bot_replica.entity.admin import *
from src.bot_replica.entity.chat import *
from src.bot_replica.entity.announcement import *


class DB:
    __db: MySQLDatabase

    @staticmethod
    def get_default_db():
        return DB.__db

    @staticmethod
    def connect_to_mysql():
        try:
            DB.__db = MySQLDatabase(
                database=os.getenv("MYSQL_DATABASE_NAME"),
                host=os.getenv("MYSQL_DATABASE_HOST"),
                user=os.getenv("MYSQL_DATABASE_USER"),
                password=os.getenv("MYSQL_DATABASE_PASSWORD"),
                port=os.getenv("MYSQL_DATABASE_PORT"),
                charset="utf8",
            )
        except Exception as e:
            print("Uzak sunucuya bağlanılamıyor. \n {}".format(e))

    @staticmethod
    def migrate():
        with DB.__db:
            DB.__db.create_tables([
                Admin,
                Announcement,
                Chat
            ])

    @staticmethod
    def init():
        DB.connect_to_mysql()
        DB.migrate()
