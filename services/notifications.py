from typing import Optional
import telebot
import json
from markdownify import markdownify

from config import settings
from models.user import User
from draftjs_exporter.dom import DOM
from draftjs_exporter.html import HTML
from models.posts import PostInDB, Post
from services.db.deta.postsDB import update_post_db
from services.db.deta.configDB import get_chat_ids, get_config
from draftjs_exporter.defaults import BLOCK_MAP, STYLE_MAP
from draftjs_exporter.constants import BLOCK_TYPES, ENTITY_TYPES, INLINE_STYLES

bot = telebot.TeleBot(get_config("telegram_bot_token"), parse_mode="MARKDOWN")

def entity_fallback(props): return DOM.create_element("p", {}, props["children"])

markdown_exporter = HTML({'block_map': dict(BLOCK_MAP, **{BLOCK_TYPES.FALLBACK : 'p',}), 'style_map': dict(STYLE_MAP, **{INLINE_STYLES.FALLBACK: 'p'}),'entity_decorators': { ENTITY_TYPES.FALLBACK: entity_fallback }})


async def send_telegram_message(chat_id, notification) -> Optional[telebot.types.Message]:
    try: return bot.send_message(chat_id, notification)
    except Exception: return False


async def send_email(email) -> bool: pass


def generate_post_message_for_tg(post: PostInDB)->str:
    content = markdownify(markdown_exporter.render(json.loads(post.content)))
    content = remove_multiple_line_breaks_from_string(str(content))
    if post.responses and len(post.responses) > 0:
        for response in post.responses:
            content += "\n\n === \n"
            _response = markdownify(markdown_exporter.render(json.loads(response.content)))
            content += f"{_response}"
    return f"id: {post.key}\n\n ⚠️⚠️ NEW GRIEVANCE POST ⚠️⚠️ \n\n**{post.subject}**\n--\n{content}"


async def notify_on_new_post(post: PostInDB):
    # Send Telegram Notification
    notification = generate_post_message_for_tg(post)
    try:
        chats = get_chat_ids()
        post.telegram = [] if not post.telegram else post.telegram
        for chat_id in chats:
            message = await send_telegram_message(chat_id, notification)
            if message: post.telegram.append({"message_id": message.message_id, "chat_id": message.chat.id})
        await update_post_db(post)
    except Exception as e:
        print(e)

    # Send Email Notification
    return True


async def notify_user(user: User) -> bool: pass


async def notify_on_new_response(post: PostInDB, response_id: int):
    notification = generate_post_message_for_tg(post)
    if notification and post.telegram:
        for chat in post.telegram: bot.edit_message_text(chat_id=chat.chat_id, message_id=chat.message_id, text=notification)
    return True


async def notify_on_delete_post(post: Post): pass


async def notify_on_delete_response(post: PostInDB, res_key): pass


async def notify_on_priority_change(post: PostInDB): pass


async def notify_on_new_user(user: User): pass


async def notify_on_login(user: User): pass


async def notify_on_password_change(user: User): pass


def remove_multiple_line_breaks_from_string(string: str):
    while string.find('\n\n') == -1: string = string.replace('\n\n', '\n')
    return string
