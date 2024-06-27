from fastapi import APIRouter


router = APIRouter()


@router.get("/healthcheck", tags=["Health check"])
def check_app_health():
    pass

