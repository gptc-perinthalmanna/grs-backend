import fastapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from api import auth, routes
from config import settings
import uvicorn


app = fastapi.FastAPI(title="GRS",

                      description="Grievance Redress  system",
                      version="0.1.0",
                      license_info={
                          "name": "Apache 2.0",
                          "url": "https://www.apache.org/licenses/LICENSE-2.0.html"},
                     )



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


def configure_routing():
    app.mount('/static', StaticFiles(directory='static'), name='static')
    app.include_router(auth.router)
    app.include_router(routes.router)


if __name__ == '__main__':
    configure()
    uvicorn.run("main:app", port=8000, host="127.0.0.1", reload=True)
else:
    configure()
