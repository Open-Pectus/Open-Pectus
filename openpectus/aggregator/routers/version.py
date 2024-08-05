from fastapi import APIRouter

from openpectus import __version__, build_number

router = APIRouter(tags=["version"], include_in_schema=False)

@router.get("/version")
def get_version():
    return __version__

@router.get("/build_number")
def get_build_number():
    return build_number
