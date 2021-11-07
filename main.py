import fastapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from api import auth, routes, posts, admin
from config import settings
import uvicorn
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from decouple import config

app = fastapi.FastAPI(title="GRS", description="Grievance Redress system", version="0.1.0")
sentry_sdk.init(dsn=config('SENTRY_DSN'))


def configure():
    configure_middlewares()
    configure_routing()


def configure_middlewares():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SentryAsgiMiddleware)


def configure_routing():
    app.mount('/static', StaticFiles(directory='static'), name='static')
    app.include_router(auth.router)
    app.include_router(routes.router)
    app.include_router(posts.router)
    app.include_router(admin.router)


if __name__ == '__main__':
    configure()
    uvicorn.run("main:app", port=8001, host="127.0.0.1", reload=True)
else:
    configure()
