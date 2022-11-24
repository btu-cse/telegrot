import os
import urllib3

from src.common.logger import Logger
from src.common.db import DB
from src.bot_replica.replica_class import ReplicaTelegramBot
from src.common.utils.migrator import migrator
from src.common.utils.env_loader import load_env

load_env()

mode = os.getenv("MODE", "dev")

# if there are warnings in HTTP request, this clears that warnings
urllib3.disable_warnings()

Logger.init()

migrator(DB().get_default_db())

replica = ReplicaTelegramBot(
    token=os.getenv("TOKEN", ""),
    mode=mode
)
