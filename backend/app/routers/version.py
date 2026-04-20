from fastapi import APIRouter, Depends
from typing import Annotated
from app.version import get_version, get_commit_hash
from app.dependencies.auth import get_current_user

router = APIRouter()


@router.get("/version")
def version(current_user: Annotated[dict, Depends(get_current_user)] = None):
    return {"version": get_version(), "commit_hash": get_commit_hash()}
