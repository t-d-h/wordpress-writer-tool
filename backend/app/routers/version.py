from fastapi import APIRouter
from app.version import get_version, get_commit_hash

router = APIRouter()


@router.get("/version")
def version():
    return {"version": get_version(), "commit_hash": get_commit_hash()}
