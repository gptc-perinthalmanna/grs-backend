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
    posts = posts_db.fetch(limit=25, last=last_key, query=query)
    response = []
    for post in posts.items:
        if not post['deleted']:
            response.append(PostInDB(**post))
    return response


async def create_new_post_db(post: Post) -> Optional[PostInDB]:
    return PostInDB(**(posts_db.insert(PostSerialized(**post.dict()).dict())))


async def put_post_to_db(post: PostInDB) -> Optional[PostInDB]:
    return PostInDB(**(posts_db.put(PostSerialized(**post.dict()).dict())))
