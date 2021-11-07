import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic.types import UUID4
from starlette import status
from models.user import AccountType, UserInDB, User
from models.posts import PostInDB, NewResponse, PostResponse, Status
from services.data_migration import convert_staffs_csv_to_pydantic, convert_students_csv_to_pydantic, remove_all_users_from_db
from services.db.deta.configDB import put_chat_id
from services.db.deta.postsDB import get_all_posts_from_db, get_post_from_id, put_post_to_db
from services.db.deta.userDB import get_all_users_from_db, get_user_from_id, get_user_from_username_db
from services.notifications import notify_on_new_response
from services.user import create_new_user, get_current_active_user, populate_fields
from constants.permissions import admin_access_permission
router = APIRouter()

tagnames = ['Admin']


@router.get("/admin/all-users/", response_model=List[UserInDB], tags=tagnames)
async def get_all_users(current_user: User = Depends(get_current_active_user)):
    if not current_user.type in admin_access_permission:
        raise HTTPException(status_code=403, detail="Admin access only")
    return await get_all_users_from_db()


@router.get("/admin/user/{user_id}/", response_model=UserInDB, tags=tagnames)
async def get_user_details(user_id: UUID4, current_user: User = Depends(get_current_active_user)):
    if not current_user.type in admin_access_permission:
        raise HTTPException(status_code=403, detail="Admin access only")
    return await get_user_from_id(user_id)


@router.get("/admin/user_from_username/{username}/", response_model=UserInDB, tags=tagnames)
async def get_user_details_from_username(username: str, current_user: User = Depends(get_current_active_user)):
    if not current_user.type in admin_access_permission:
        raise HTTPException(status_code=403, detail="Admin access only")
    return await get_user_from_username_db(username)


@router.post("/admin/new_response_for_user/{user_id}/", response_model=PostInDB, tags=tagnames)
async def post_new_response_on_behalf_of_another_user(user_id: UUID4, response: NewResponse, current_user: User = Depends(get_current_active_user)):
    if not current_user.type in admin_access_permission:
        raise HTTPException(status_code=403, detail="Admin access only")
    post = await get_post_from_id(response.post_key)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found!")
    user = await get_user_from_id(user_id)
    response_to_save = PostResponse(
        id=len(post.responses) if post.responses else 0, author=user.key, content=response.content, modified=datetime.datetime.now(), published=datetime.datetime.now(),
        statusChange={ 'prev': post.status, 'to': response.status }
    )
    post.modified = datetime.datetime.now()
    post.status = response.status

    if post.responses is None:
        post.responses = [response_to_save]
    else:
        post.responses.append(response_to_save)

    await notify_on_new_response(post, response_to_save.id)
    return await put_post_to_db(post)


@router.post("/admin/add_users_from_csv/{type}/", tags=tagnames)
async def add_users_from_csv(type: str, file: bytes = File(...), current_user: User = Depends(get_current_active_user)):
    if not current_user.type in admin_access_permission:
        raise HTTPException(status_code=403, detail="Admin access only")
    user_list = []
    if type == 'student':
        user_list = convert_students_csv_to_pydantic( file.decode("utf-8").splitlines() )
    elif type == 'staff':
        user_list = convert_staffs_csv_to_pydantic( file.decode("utf-8").splitlines() )
    else:
        raise HTTPException(status_code=400, detail="Invalid type")

    message = []
    for user in user_list:
        try:
            _user = populate_fields(user)
            if await get_user_from_username_db(_user.username):
                message.append(f"User {_user.username} already exists")
                continue
            await create_new_user(_user)
            message.append(f"{user.username} added successfully")
            print(f"{user.username} added successfully")
        except Exception as e:
            message.append(f"{user.username} - {e}")
            print(f"{user.username} - {e}")
    
    return {'message': message }


@router.get("/admin/test/", include_in_schema=False)
async def test_route(current_user: User = Depends(get_current_active_user)):
    if not current_user.type in admin_access_permission:
        raise HTTPException(status_code=403, detail="Admin access only")
    await remove_all_users_from_db()
    return {'message': 'test route'}


@router.get("/admin/reports/posts")
async def get_post_reports(current_user: User = Depends(get_current_active_user)):
    if not current_user.type in admin_access_permission:
        raise HTTPException(status_code=403, detail="Admin access only")
    status_report = {}
    user_post_map = {}
    this_day = {}
    this_week = {}
    this_month = {}
    this_year = {}
    user_type_report = {}

    # Fetch all posts from DB
    all_posts, last, total_posts = await get_all_posts_from_db(skip_deleted=False)
    while last:
        _posts, last, count = await get_all_posts_from_db(last_key=last, skip_deleted=False)
        total_posts += count
        all_posts += _posts
    # Grenerate Blank Status Report
    status_report['total_posts'] = total_posts
    for status in Status:
        status_report[status.name] = 0
        this_day[status.name] = 0
        this_month[status.name] = 0
        this_week[status.name] = 0
        this_year[status.name] = 0

    for post in all_posts:
        status_report[post.status.name] += 1
        if post.author.hex not in user_post_map:
            user_post_map[post.author.hex] = {"user": None, "posts": []}
        user_post_map[post.author.hex]["posts"].append(post)

        if post.modified >=  datetime.datetime.now() - datetime.timedelta(days=1):
            this_day[post.status.name] += 1
        if post.modified >=  datetime.datetime.now() - datetime.timedelta(days=7):
            this_week[post.status.name] += 1
        if post.modified >=  datetime.datetime.now() - datetime.timedelta(days=30):
            this_month[post.status.name] += 1
        if post.modified >=  datetime.datetime.now() - datetime.timedelta(days=365):
            this_year[post.status.name] += 1
    
    for user_type in AccountType:
        user_type_report[user_type.name] = {"open": 0, "closed": 0, "total": 0}
    for user in user_post_map.keys():
        user_obj = await get_user_from_id(UUID4(user))
        if not user_obj:
            continue
        # user_post_map[user]["user"] = user_obj
        user_type_report[user_obj.type]["total"] += 1
        for post in user_post_map[user]["posts"]:
            if post.status == Status.open:
                user_type_report[user_obj.type]["open"] += 1
            elif post.status == Status.closed:
                user_type_report[user_obj.type]["closed"] += 1

    return {"posts" : {"all" : status_report, "this_day" :  this_day, "this_week": this_week, "this_month":this_month, "this_year":this_year}, "users": user_type_report}


@router.post("/admin/connections/telegram/add-chat/{chat_id}/", tags=tagnames)
async def add_telegram_chat(chat_id: str, current_user: User = Depends(get_current_active_user)):
    if not current_user.type in admin_access_permission:
        raise HTTPException(status_code=403, detail="Admin access only")
    
    put_chat_id(chat_id)
    return {"message": "Chat added successfully"}