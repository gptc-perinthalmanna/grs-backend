from starlette import status
from fastapi import HTTPException
from models.user import AccountType

admin_access_permission = ['admin']

post_permissions = {
    'post_view': [AccountType.grievance_cell_memeber],
    'post_edit': [AccountType.grievance_cell_memeber],
    'post_respond': [AccountType.grievance_cell_memeber, AccountType.parent],
    'post_delete': [AccountType.grievance_cell_memeber],
    'response_delete': [AccountType.grievance_cell_memeber]
}

no_permission = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have permissions for this action!")