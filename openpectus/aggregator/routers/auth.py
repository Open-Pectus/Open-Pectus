import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["auth"])
router = APIRouter(tags=['auth'])

class AuthConfig(BaseModel):
    authority_url: str
    client_id: str

@router.get('/config')
def get_config() -> AuthConfig:
    return AuthConfig(
        authority_url=os.getenv('AUTH_AUTHORITY_URL'),
        client_id=os.getenv('AUTH_WEB_FRONTEND_CLIENT_ID')
    )
