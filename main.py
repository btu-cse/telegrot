import os
import urllib3

from src.common.logger import Logger
from src.common.db import DB
from src.bot_replica.replica_class import ReplicaTelegramBot
from src.common.utils.migrator import migrator
from src.common.utils.env_loader import load_env
from src.common import constants

print("Initializing...")

# if there are warnings in HTTP request, this clears that warnings
urllib3.disable_warnings()

load_env()

migrator(DB().get_default_db())


def main():
    mode = os.getenv("MODE", constants.DEFAULT_MODE)
    bot_type = os.getenv("BOT_TYPE", constants.DEFAULT_BOT_TYPE)

    if bot_type == constants.BOT_TYPE_REPLICA:
        replica = ReplicaTelegramBot(
            token=os.getenv("REPLICA_BOT_TOKEN", ""),
            mode=mode,
            control_key=os.getenv("REPLICA_CONTROL_KEY",
                                  constants.DEFAULT_CONTROL_KEY),
            web_hook_url=os.getenv("REPLICA_WEB_HOOK_URL", ""),
            port=int(os.getenv("REPLICA_PORT", constants.DEFAULT_PORT)),
        )
    elif bot_type == constants.BOT_TYPE_INTRODUCTION:
        # TODO: this will be implemented
        pass
    else:
        Logger.fatal("{} bot type is not supported".format(bot_type))


if __name__ == "__main__":
    main()
