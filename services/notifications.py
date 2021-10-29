import telebot
import json
from markdownify import markdownify

from models.posts import PostInDB, Post
from models.user import User
from services.db.deta.telegramDB import get_chat_id
from draftjs_exporter.html import HTML
from draftjs_exporter.dom import DOM
from draftjs_exporter.defaults import BLOCK_MAP, STYLE_MAP
from draftjs_exporter.constants import BLOCK_TYPES, ENTITY_TYPES, INLINE_STYLES


bot = telebot.TeleBot("2090757545:AAF00DXNp4vj_lxDeugKPG0MHgeb2zJ0kDI", parse_mode="MARKDOWN")

def entity_fallback(props):
     return DOM.create_element(
        "p", {}, props["children"]
    )
markdown_exporter = HTML({'block_map': dict(BLOCK_MAP, **{
    BLOCK_TYPES.FALLBACK : 'p',
}), 'style_map': dict(STYLE_MAP, **{INLINE_STYLES.FALLBACK: 'p'}),
'entity_decorators': { ENTITY_TYPES.FALLBACK: entity_fallback 
}})




async def send_telegram_message(notification) -> bool:
    try:
        chat_id = get_chat_id()
        bot.send_message(chat_id, notification)
        return True
    except Exception:
        return False


async def send_email(email) -> bool:
    pass


async def notify_on_new_post(post: PostInDB):
    # Send Telegram Notification

    content = markdownify(markdown_exporter.render(json.loads(post.content)))
    notification = f"*{post.title}*\n\n{content}"
    await send_telegram_message(notification)
    return True

async def notify_user(user: User) -> bool:
    pass


async def notify_on_new_response(post: PostInDB, response_id: int):
    pass


async def notify_on_delete_post(post: Post):
    pass


async def notify_on_delete_response(post: PostInDB, res_key):
    pass


async def notify_on_priority_change(post: PostInDB):
    pass


async def notify_on_new_user(user: User):
    pass


async def notify_on_login(user: User):
    pass


async def notify_on_password_change(user: User):
    pass

