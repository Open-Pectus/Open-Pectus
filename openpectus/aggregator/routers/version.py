from fastapi import APIRouter

from openpectus import __version__

router = APIRouter(tags=["version"], include_in_schema=False)

@router.get("/version")
def get_version():
    return __version__
