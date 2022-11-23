import os
import sys

from dotenv import load_dotenv


def load_env(path=os.path.join(sys.path[0], '.env')):
    load_dotenv(path)
