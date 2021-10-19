from models.posts import PostInDB, Post
from models.user import User


async def send_telegram_message(notification) -> bool:
    pass


async def send_email(email) -> bool:
    pass


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

