from deta import Deta
from config import settings


deta = Deta(settings.DETA_BASE_KEY)  # configure your Deta project
config_db = deta.Base('config')



def get_config(config_name):
    _config = config_db.get(config_name)
    if _config is None:
        put_config(config_name, {})
        return {}
    return _config

def put_config(config_name, config_value):
    config_db.put(config_value, config_name)

def get_chat_ids():
    bot_config = get_config("telegram")
    if bot_config is None:
        put_config("telegram", {"telegram_connected_chats": []})
        return []
    return bot_config["telegram_connected_chats"]

def put_chat_id(chat_id):
    new_config =  get_config("telegram")
    if new_config["telegram_connected_chats"] is None: new_config["telegram_connected_chats"] = []
    new_config["telegram_connected_chats"].append(chat_id)
    put_config("telegram", new_config)
