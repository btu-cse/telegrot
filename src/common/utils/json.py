from json import JSONEncoder

from src.bot_replica.entity.chat import Chat

def json_dumper(obj):
    try:
        return obj.toJSON()
    except:
        pass
