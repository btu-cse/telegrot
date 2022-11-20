import os
import urllib3
import sys

from src.utils.logger import Logger
from src.utils.db import DB

mode = os.getenv("MODE")

# if there are warnings in HTTP request, this clears that warnings
urllib3.disable_warnings()

Logger.init()

DB.init()