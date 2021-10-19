from fastapi import responses, APIRouter
router = APIRouter()


@router.get('/', include_in_schema=False)
def index():
    return responses.RedirectResponse(url='/redoc')


@router.get('/favicon.ico', include_in_schema=False)
def favicon():
    return responses.RedirectResponse(url='/static/icons/favicon.ico')