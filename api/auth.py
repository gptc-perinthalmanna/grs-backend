from datetime import timedelta
from fastapi import Depends, HTTPException, APIRouter, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.types import UUID4
from starlette import status
from models.user import AccountType, BasicUser, CustomUserCreate, User, Token, UserCreate, UserEdit, ChangePassword
from services.db.deta.userDB import get_user_from_id, get_user_from_username_db, permanently_delete_user_from_db
from services.notifications import notify_on_password_change, notify_on_new_user
from services.user import authenticate_user, create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES, \
    create_new_user, get_user_details_from_pen_number, get_user_details_from_student_id, update_user_fields, check_password_and_username, send_email, generate_password_reset_token, \
    verify_password_reset_token, get_user, populate_fields, update_user_password

router = APIRouter()


@router.post("/token", response_model=Token, tags=['User'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"}, )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data=user, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=User, tags=['User'])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user.
    """
    return current_user


@router.post("/users/new/", response_model=User, tags=['User'])
async def create_user(new_user: UserCreate):
    """
       Create new user.
    """
    # if not config.USERS_OPEN_REGISTRATION:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Open user resistration is forbidden on this server",
    #     )
    new_user = populate_fields(new_user)
    user = await get_user(new_user.username)
    if user:
        raise HTTPException(status_code=400,detail="The user with this username already exists in the system.",)
    user = await create_new_user(new_user)
    await notify_on_new_user(user)
    return user


@router.post("/custom/register/", response_model=User, tags=['User'])
async def register_user_from_server_data(user_create: CustomUserCreate, account_id: int):
    """
    Create new user from server data.
    """
    if user_create.account_type == AccountType.student:
        new_user = get_user_details_from_student_id(account_id)
    elif user_create.account_type == AccountType.teacher:
        new_user = get_user_details_from_pen_number(account_id)
    else:
        raise HTTPException(status_code=400,detail="Invalid account type.")

    user = await get_user_from_username_db(new_user.username)
    if user:
        raise HTTPException(status_code=400,detail="The user with this account already exists in the system.",)

    # TODO : Send Verification Email
    # TODO : Add Verification Route
    # TODO : Add user email to verification queue with timeout

    user = await create_new_user(new_user)
    await notify_on_new_user(user)
    return user


@router.put("/users/me/edit/", response_model=User, status_code=status.HTTP_202_ACCEPTED, tags=['User'])
async def edit_user(updateuser: UserEdit, current_user: User = Depends(get_current_active_user)):
    """
       Edit user profile.
    """
    if updateuser.username != current_user.username:
        raise HTTPException(status_code=400,detail="Username cannot be changed.",)
    user = await update_user_fields(updateuser, current_user)
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="An error occured.")


@router.put("/users/me/change-password/", tags=['User'], status_code=status.HTTP_202_ACCEPTED)
async def change_password(req: ChangePassword, current_user: User = Depends(get_current_active_user)):
    if not await check_password_and_username(req, current_user):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="Incorrect username or password")
    if not req.new_password == req.repeat_password:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail="Entered password doesn't match")
    if await update_user_password(req.new_password, current_user):
        await notify_on_password_change(current_user)
        return {"message": "Password Successfully changed!"}
    else:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT,detail="An unknown error occured.")


@router.post("/users/forgot/", tags=['User'])
async def forgot_password(email: str, username: str, background_tasks: BackgroundTasks):
    # verify email on db
    # verify username on db
    reset_password_token = generate_password_reset_token(username)
    # send email
    background_tasks.add_task(send_email, email, subject='Forgot password Request',
                              message=f'Post new_password to this link to '
                                      f'reset password : '
                                      f'http://localhost:8000/users/forgot/reset/{reset_password_token}')
    # generate token
    return {"message": "An email send to your email address with reset password link"}


@router.post("/users/forgot/reset/{reset_password_token}", status_code=status.HTTP_202_ACCEPTED, tags=['User'])
async def reset_password_link(reset_password_token: str, new_password: str, repeat_password: str):
    username = verify_password_reset_token(reset_password_token)
    if not username:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await get_user(username)
    if not user:
        raise HTTPException(status_code=404,detail="The user with this username does not exist in the system.")
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    if new_password != repeat_password:
        raise HTTPException(status_code=400,detail="Password doesnot match")
    if await update_user_password(new_password, user):
        await notify_on_password_change(user)
        return reset_password_token
    else:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT,detail="An unknown error occured.")


@router.get("/users/user/{user_id}/", response_model=BasicUser, tags=["User"])
async def get_user_details(user_id: UUID4, current_user: User = Depends(get_current_active_user)):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are blocked from the system")
    user = await get_user_from_id(user_id)
    return BasicUser(**user.dict())


# Test Routes
@router.delete("/users/{username}/", include_in_schema=False)
async def delete_user(username):
    from test_main import user
    if username == user['username']:
        userd = await get_user(username)
        if userd is None:
            return "User didn't Exists"
        await permanently_delete_user_from_db(userd)
        return "success"
    else:
        return "Invalid Operation"