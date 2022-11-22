import os
import urllib3
import sys

from dotenv import load_dotenv


def load_env(path=os.path.join(sys.path[0], '.env')):
    print(path)
    load_dotenv(path)
