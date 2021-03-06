import datetime, uuid
from starlette import status
from pydantic import UUID4, BaseModel
from typing import List, Optional, Union
from fastapi import Depends, HTTPException, APIRouter, Request

from models.user import User
from services.user import get_current_active_user
from models.posts import Post, PostInDB, PostResponse, NewResponse, NewPost, Status
from constants.permissions import admin_access_permission, post_permissions as permissions, no_permission
from services.notifications import notify_on_new_post, notify_on_new_response, notify_on_delete_post, notify_on_delete_response
from services.db.deta.postsDB import get_my_posts_from_db, get_post_from_id, get_all_posts_from_db, create_new_post_db, put_post_to_db

router = APIRouter()
tag = 'Posts'


class FetchQuery(BaseModel):
    last_key: Optional[UUID4] = None
    query: Union[dict, list] = None


class PostListWithKey(BaseModel):
    posts: List[PostInDB]
    last_key: Optional[UUID4]
    count: int


@router.post('/posts/all/', response_model=PostListWithKey, tags=[tag])
async def get_all_posts(key: Optional[FetchQuery] = None, current_user: User = Depends(get_current_active_user)):
    if current_user.type not in permissions['post_view']:
        raise no_permission
    if not key:
        posts, last_key, count =  await get_all_posts_from_db()
        return PostListWithKey(posts=posts, last_key=last_key, count=count)
    posts, last_key, count = await get_all_posts_from_db(last_key=key.last_key, query=key.query)
    return PostListWithKey(posts=posts, last_key=last_key, count=count)


@router.get('/posts/me/', response_model=PostListWithKey, tags=[tag])
async def get_my_posts(key: Optional[UUID4] = None, current_user: User = Depends(get_current_active_user)):
    posts, last, count = await get_my_posts_from_db(user_id=current_user.key, last_key=key)
    return PostListWithKey(posts=posts, last_key=last, count=count)


@router.get('/posts/{post_id}/', response_model=PostInDB, tags=[tag])
async def get_post(post_id: UUID4, current_user: User = Depends(get_current_active_user)):
    post = await get_post_from_id(post_id)
    if current_user.key != post.author and current_user.type not in permissions['post_view']:
        raise no_permission
    if not post:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="Post not Exists")
    if post.deleted or not post.visible:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="Post is not accessible")
    return post


@router.post('/posts/new/', response_model=PostInDB, tags=[tag])
async def create_post(post: NewPost, current_user: User = Depends(get_current_active_user)):
    _post = Post(
        key=uuid.uuid4(),
        status=Status.open,
        author=current_user.key,
        authorName=current_user.username,
        published=datetime.datetime.now(),
        modified=datetime.datetime.now(),
        **post.dict()
    )
    new_post = await create_new_post_db(_post)
    await notify_on_new_post(new_post)
    return new_post


@router.delete('/posts/{key}/', tags=[tag])
async def delete_post(key: UUID4, current_user: User = Depends(get_current_active_user)):
    post = await get_post_from_id(key)
    if post.author != current_user.key and current_user.type not in permissions['post_delete']: raise no_permission
    post.deleted = True
    post.visible = False
    post.status = Status.deleted
    post.modified = datetime.datetime.now()
    await put_post_to_db(post)
    await notify_on_delete_post(post)
    return "Post Successfully Deleted."


@router.post('/posts/response/new/', tags=[tag])
async def new_response_to_post(response: NewResponse,request:Request, current_user: User = Depends(get_current_active_user)):
    print(request.body)
    post = await get_post_from_id(response.post_key)
    if not post: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found!")
    if post.author != current_user.key and current_user.type not in permissions['post_respond']: raise no_permission

    if response.user_id:
        user_id = response.user_id if current_user.type in admin_access_permission else current_user.key
    else:
        user_id = current_user.key

    response_to_save = PostResponse(
        id=len(post.responses) if post.responses else 0, author=user_id, content=response.content, modified=datetime.datetime.now(), published=datetime.datetime.now(),
        statusChange={ 'prev': post.status, 'to': response.status }
    )
    post.modified = datetime.datetime.now()
    post.status = response.status

    if post.responses is None: post.responses = [response_to_save]
    else: post.responses.append(response_to_save)

    await notify_on_new_response(post, response_to_save.id)
    return await put_post_to_db(post)


@router.delete('/posts/{key}/response/{res_id}/', tags=[tag])
async def delete_response_of_post(key: UUID4, res_id: int, current_user: User = Depends(get_current_active_user)):
    post = await get_post_from_id(key)

    if post.responses is None or post.responses[res_id] is None: raise HTTPException( status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Response not found.')

    if current_user.type not in permissions['response_delete'] and post.responses[res_id].author != current_user.key: raise no_permission

    post.responses[res_id].deleted = True
    post.responses[res_id].visible = False
    # Change post id to previous if last response is deleted. Only Temporary solution - If multiple posts is deleted
    # then it fails.
    if len(post.responses) == res_id: post.status = post.responses[res_id].statusChange.prev
    post = await put_post_to_db(post)
    await notify_on_delete_response(post, res_id)
    return post
 