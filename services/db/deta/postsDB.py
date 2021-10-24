from typing import Optional, List, Union

from deta import Deta
from pydantic import UUID4

from config import settings
from models.posts import Post, PostSerialized, PostInDB

from models.user import User, UserInDB, UserSerialized

deta = Deta(settings.DETA_BASE_KEY)  # configure your Deta project
posts_db = deta.Base('posts')


async def get_post_from_id(key: UUID4) -> Optional[PostInDB]:
    post = posts_db.get(key.hex)
    if post:
        return PostInDB(**post)
    else:
        return None


async def get_all_posts_from_db(last_key: Optional[UUID4] = None, query: Union[dict, list] = None) -> Optional[
    List[PostInDB]]:
    lk = last_key.hex if last_key else None
    posts = posts_db.fetch(limit=25, last=lk, query=query)
    response = []
    for post in posts.items:
        if not post['deleted']:
            response.append(PostInDB(**post))
    return response, posts.last, posts.count


async def get_my_posts_from_db(user_id: UUID4, last_key: Optional[UUID4] = None) -> Optional[
    List[PostInDB]]:
    lk = last_key.hex if last_key else None
    posts = posts_db.fetch(limit=25, last=lk, query={"author": user_id.hex})
    response = []
    for post in posts.items:
        if not post['deleted']:
            response.append(PostInDB(**post))
    while posts.last and len(response) < 10:
        posts = posts_db.fetch(limit=15, last=posts.last, query={"author": user_id.hex})
        for post in posts.items:
            if not post['deleted']:
                response.append(PostInDB(**post))

    return response, posts.last, posts.count



async def create_new_post_db(post: Post) -> Optional[PostInDB]:
    return PostInDB(**(posts_db.insert(PostSerialized(**post.dict()).dict())))


async def put_post_to_db(post: PostInDB) -> Optional[PostInDB]:
    return PostInDB(**(posts_db.put(PostSerialized(**post.dict()).dict())))


async def delete_post_permanently_db(post_key):
    return posts_db.delete(post_key)
