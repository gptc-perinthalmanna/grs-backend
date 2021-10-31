from starlette import status
from fastapi import HTTPException
from models.user import AccountType

admin_access_permission = ['admin', 'staff']

post_permissions = {
    'post_view': [AccountType.staff],
    'post_edit': [AccountType.staff],
    'post_respond': [AccountType.staff, AccountType.parent],
    'post_delete': [AccountType.staff],
    'response_delete': [AccountType.staff]
}

no_permission = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have permissions for this action!")