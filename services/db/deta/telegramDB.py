from deta import Deta
from config import settings


deta = Deta(settings.DETA_BASE_KEY)  # configure your Deta project
telegram_db = deta.Base('telegram_db')


def get_chat_id():
    bot_config = telegram_db.get("bot_config")
    return bot_config["connected_chats"]