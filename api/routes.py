from fastapi import responses, APIRouter
router = APIRouter()


@router.get('/', include_in_schema=False)
def index():
    return responses.RedirectResponse(url='/docs')


@router.get('/favicon.ico', include_in_schema=False)
def favicon():
    return responses.RedirectResponse(url='/static/icons/favicon.ico')


@router.get('/errortest/', include_in_schema=False)
def error_test():
    a = 12/0
    return "Ok"