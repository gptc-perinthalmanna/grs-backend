import datetime
from typing import List, Optional, Union

from fastapi import Depends, HTTPException, APIRouter
from pydantic import UUID4, BaseModel
from starlette import status

from models.posts import Post, PostInDB, PostResponse, NewResponse
from models.user import User, AccountType
from services.db.deta.postsDB import get_post_from_id, get_all_posts_from_db, create_new_post_db, put_post_to_db
from services.user import get_current_active_user

router = APIRouter()

tag = 'Posts'
permissions = {
    'post_view': [AccountType.staff],
    'post_edit': [AccountType.staff],
    'post_respond': [AccountType.staff, AccountType.parent],
    'post_delete': [AccountType.staff]
}
no_permission = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                              detail="You don't have permissions for this action!")


@router.get('/posts/{post_id}/', response_model=PostInDB, tags=[tag])
async def get_post(post_id: UUID4, current_user: User = Depends(get_current_active_user)):
    post = await get_post_from_id(post_id)
    if current_user.key != post.author and current_user.type not in permissions['post_view']:
        raise no_permission
    if not post:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Post not Exists")
    if post.deleted or not post.visible:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Post is not accessible")
    return post


class FetchQuery(BaseModel):
    last_key: Optional[UUID4] = None
    query: Union[dict, list] = None


@router.post('/posts/all', response_model=List[PostInDB], tags=[tag])
async def get_all_posts(key: Optional[FetchQuery] = None, current_user: User = Depends(get_current_active_user)):
    if current_user.type not in permissions['post_view']:
        raise no_permission
    if not key:
        return await get_all_posts_from_db()
    return await get_all_posts_from_db(last_key=key.last_key, query=key.query)


@router.post('/posts/new', response_model=PostInDB, tags=[tag])
async def create_post(post: Post, current_user: User = Depends(get_current_active_user)):
    return await create_new_post_db(post)


@router.delete('/posts/{key}', tags=[tag])
async def delete_post(key: UUID4, current_user: User = Depends(get_current_active_user)):
    post = await get_post_from_id(key)
    if post.author != current_user.key and current_user.type not in permissions['post_delete']:
        raise no_permission
    post.deleted = True
    post.visible = False
    post.modified = datetime.datetime.now()
    await put_post_to_db(post)
    return "Post Successfully Deleted."


@router.post('/post/{key}/responses/new/', tags=[tag])
async def new_response_to_post(response: NewResponse, current_user: User = Depends(get_current_active_user)):
    post = await get_post_from_id(response.post_key)
    if post.author != current_user.key and current_user.type not in permissions['post_respond']:
        raise no_permission
    response_to_save = PostResponse()
    response_to_save.id = len(post.responses) + 1
    response_to_save.content = response.content
    response_to_save.modified = datetime.datetime.now()
    response_to_save.published = datetime.datetime.now()
    response_to_save.statusChange = {
        'prev': post.status,
        'to': response.status
    }
    post.modified = datetime.datetime.now()
    post.responses.append(response_to_save)
    await put_post_to_db(post)
