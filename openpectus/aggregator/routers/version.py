from fastapi import APIRouter

from openpectus import __version__, build_number, build_info
from openpectus.aggregator.routers.dto import BuildInfo

router = APIRouter(tags=["version"])

@router.get("/version", response_model_exclude_none=True)
def get_version():
    return __version__

@router.get("/build_number", response_model_exclude_none=True)
def get_build_number():
    return build_number

@router.get("/api/build_info", response_model_exclude_none=True)
def get_build_info() -> BuildInfo:
    return build_info
