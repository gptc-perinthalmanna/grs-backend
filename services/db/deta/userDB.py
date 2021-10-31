from typing import List, Optional

from deta import Deta
from pydantic import UUID4

from config import settings

from models.user import User, UserInDB, UserSerialized

deta = Deta(settings.DETA_BASE_KEY)  # configure your Deta project
users_db = deta.Base('users')


async def get_user_from_id(key: UUID4) -> Optional[UserInDB]:
    user = users_db.get(key.hex)
    if user:
        return UserInDB(**user)
    else:
        return None


async def get_user_from_username_db(username: str) -> Optional[UserInDB]:
    fetch = users_db.fetch({'username': username}, limit=1)
    if fetch.count > 0:
        user = fetch.items[0]
        return UserInDB(**user)
    else:
        return None


async def create_new_user_to_db(user: UserInDB) -> UserInDB:
    user = users_db.insert(UserSerialized(**user.dict()).dict())
    return UserInDB(**user)


async def update_user_to_db(user: User, userindb: UserInDB) -> Optional[UserInDB]:
    var = userindb.dict()
    var.update(**{k: v for k, v in user.dict().items() if v is not None})
    var1 = UserInDB(**var)
    userdb = users_db.put(var1.dict())
    if userdb:
        return UserInDB(**userdb)
    else:
        return None


async def update_password_to_db(hashed_password, userindb: User) -> UserInDB:
    v = userindb.dict()
    v['hashed_password'] = hashed_password
    return users_db.put(v, key=userindb.key)


async def permanently_delete_user_from_db(user):
    return users_db.delete(UserSerialized(**user.dict()).key)


async def get_all_users_from_db() -> Optional[List[UserInDB]]:
    users = users_db.fetch()
    if users.count > 0:
        return [UserInDB(**user) for user in users.items]
    else:
        return []
