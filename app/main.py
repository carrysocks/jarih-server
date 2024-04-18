from fastapi import FastAPI, Depends

from app.api.routes.api import api_router
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.db.dependencies import init_db
from app.core.middleware.cors import set_cors


def get_application() -> FastAPI:
    application = FastAPI()
    settings = get_app_settings()
    application.include_router(api_router)

    set_cors(application)

    init_db(settings.DB_URL)

    return application


app = get_application()
