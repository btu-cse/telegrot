import os
import urllib3
import sys


from src.common.logger import Logger
from src.common.db import DB
from src.bot_replica.state import ReplicaState
from src.utils.migrator import migrator
from src.utils.env_loader import load_env

load_env()

mode = os.getenv("MODE")
print(mode)
# if there are warnings in HTTP request, this clears that warnings
urllib3.disable_warnings()

Logger.init()

migrator(DB().get_default_db())

ReplicaState().migrate()
