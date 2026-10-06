import os

from fastapi import APIRouter

router = APIRouter(prefix="/databricks", tags=["databricks"])


@router.get("")
def read_env():
    return {
        "uvicorn_host": os.getenv("UVICORN_HOST", "Not defined"),
        "uvicorn_port": os.getenv("UVICORN_PORT", "Not defined"),
    }
