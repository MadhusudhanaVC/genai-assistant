from fastapi import FastAPI

from app.api.routes import register_routes
from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG == "True",
)


register_routes(app)