import os
import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/databricks", tags=["databricks"])

IDENTITY_HEADERS = [
    "X-Forwarded-Email",
    "X-Forwarded-User",
    "X-Forwarded-Preferred-Username",
    "X-Real-Ip",
    "X-Request-Id",
]


@router.get("")
def read_env():
    return {
        "uvicorn_host": os.getenv("UVICORN_HOST", "Not defined"),
        "uvicorn_port": os.getenv("UVICORN_PORT", "Not defined"),
    }


@router.get("/auth_details")
def get_auth_details(request: Request) -> JSONResponse:
    headers = {name: request.headers.get(name) for name in IDENTITY_HEADERS}
    token = request.headers.get("X-Forwarded-Access-Token")

    result = {
        "1_identity_headers": headers,
        "2_user_token_present": token is not None,
    }

    return JSONResponse(json.loads(json.dumps(result, default=str)))
