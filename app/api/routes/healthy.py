from fastapi import APIRouter

router = APIRouter(prefix="/healthy", tags=["health-check"])


@router.get("")
def healthy_check():
    return {"healthy": "ok"}
