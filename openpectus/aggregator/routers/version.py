from fastapi import APIRouter

from openpectus import __version__, build_number, build_info
from openpectus.aggregator.routers.dto import BuildInfo

router = APIRouter(tags=["version"])

@router.get("/version")
def get_version():
    return __version__

@router.get("/build_number")
def get_build_number():
    return build_number

@router.get("/api/build_info")
def get_build_info() -> BuildInfo:
    return build_info
