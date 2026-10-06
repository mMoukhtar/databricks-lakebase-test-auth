from typing import Any
import os
import json
import base64

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from databricks.sdk import WorkspaceClient

router = APIRouter(prefix="/databricks", tags=["databricks"])

IDENTITY_HEADERS = [
    "X-Forwarded-Email",
    "X-Forwarded-User",
    "X-Forwarded-Preferred-Username",
    "X-Real-Ip",
    "X-Request-Id",
]


def decode_jwt_claims(token: str) -> dict[str, Any]:
    """Decode the payload of a JWT without verifying it. For inspection only."""
    parts = token.split(".")
    if len(parts) != 3:
        return {"note": "Token is not a JWT (opaque token)"}
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception as exc:
        return {"error": f"Could not decode payload: {exc}"}


def me_with_user_token(token: str) -> dict:
    """Option 3: read the signed-in user's own profile and groups with their token."""
    resp = requests.get(
        f"{workspace_url()}/api/2.0/preview/scim/v2/Me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    if not resp.ok:
        return {"status": resp.status_code, "error": resp.text[:500]}
    data = resp.json()
    return {
        "userName": data.get("userName"),
        "displayName": data.get("displayName"),
        "emails": [e.get("value") for e in data.get("emails", [])],
        "groups": [g.get("display") for g in data.get("groups", [])],
    }


def lookup_with_service_principal(email: str) -> dict:
    """Option 2: look up the user's groups with the app's service principal."""
    try:
        # Uses DATABRICKS_CLIENT_ID / DATABRICKS_CLIENT_SECRET set by Databricks Apps
        w = WorkspaceClient()
        users = list(
            w.users.list(
                filter=f'userName eq "{email}"',
                attributes="userName,displayName,groups",
            )
        )
        if not users:
            return {
                "note": "User not found, or the service principal cannot read users"
            }
        user = users[0]
        return {
            "userName": user.user_name,
            "displayName": user.display_name,
            "groups": [g.display for g in (user.groups or [])],
        }
    except Exception as exc:
        return {"error": str(exc)[:500]}


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

    if token:
        result["2_user_token_claims"] = decode_jwt_claims(token)
        result["3_me_with_user_token"] = me_with_user_token(token)
    else:
        result["3_me_with_user_token"] = (
            "Skipped: no user token (user authorization is off)"
        )

    email = headers["X-Forwarded-Email"]
    result["4_lookup_with_service_principal"] = (
        lookup_with_service_principal(email) if email else "Skipped: no email header"
    )

    return JSONResponse(json.loads(json.dumps(result, default=str)))
