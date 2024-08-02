from fastapi import APIRouter

from openpectus import __version__

router = APIRouter(tags=["version"])

@router.get("/version")
def get_version():
    return __version__
