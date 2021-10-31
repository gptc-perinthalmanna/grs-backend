import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic.types import UUID4
from starlette import status
from models.user import UserInDB, User
from models.posts import PostInDB, NewResponse, PostResponse
from services.data_migration import convert_students_csv_to_pydantic, remove_all_users_from_db
from services.db.deta.postsDB import get_post_from_id, put_post_to_db
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
    if type == 'student':
        students_list = convert_students_csv_to_pydantic( file.decode("utf-8").splitlines() )
        # print(students_list)
        message = []
        for student in students_list:
            try:
                _student = populate_fields(student)
                await create_new_user(_student)
                message.append(f"{student.username} added successfully")
                print(f"{student.username} added successfully")
            except Exception as e:
                message.append(f"{student.username} - {e}")
                print(f"{student.username} - {e}")
        
        return {'message': message }
    else:
        raise HTTPException(status_code=400, detail="Invalid type")
    
@router.get("/admin/test/")
async def test_route():
    await remove_all_users_from_db()
    return {'message': 'test route'}