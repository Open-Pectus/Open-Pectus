import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=['auth'])

class AuthConfig(BaseModel):
    use_auth: bool
    authority_url: str | None
    client_id: str | None

@router.get('/config')
def get_config() -> AuthConfig:
    return AuthConfig(
        use_auth=os.getenv('USE_AUTH', default=False),
        authority_url=os.getenv('AUTH_AUTHORITY_URL'),
        client_id=os.getenv('AUTH_WEB_FRONTEND_CLIENT_ID')
    )
