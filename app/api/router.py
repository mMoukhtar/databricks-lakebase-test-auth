from fastapi import APIRouter

from app.api.routes import healthy
from app.api.routes import databricks

app_router = APIRouter(prefix="/api/v1")

app_router.include_router(healthy.router)
app_router.include_router(databricks.router)
