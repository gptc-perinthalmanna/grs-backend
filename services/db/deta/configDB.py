from deta import Deta
from config import settings


deta = Deta(settings.DETA_BASE_KEY)  # configure your Deta project
config_db = deta.Base('config')


def get_config(config_name):
    _config = config_db.get(config_name)
    if _config is None:
        put_config(config_name, {'value': None})
    return _config['value']

def put_config(config_name, config_value):
    config_db.put(config_value, config_name)

def get_chat_ids():
    connected_chats = get_config("telegram_connected_chats")
    if connected_chats is None:
        put_config("telegram_connected_chats", [])
        return []
    return connected_chats

def put_chat_id(chat_id):
    connected_chats =  get_config("telegram_connected_chats")
    if connected_chats is None: connected_chats = []
    connected_chats.append(chat_id)
    put_config("telegram_connected_chats", connected_chats)
