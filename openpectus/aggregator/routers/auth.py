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
    tenant_id = os.getenv('AZURE_DIRECTORY_TENANT_ID', default=None)
    authority_url = f'https://login.microsoftonline.com/{tenant_id}/v2.0' if tenant_id else None
    return AuthConfig(
        use_auth=os.getenv('ENABLE_AZURE_AUTHENTICATION', default=False),
        authority_url=authority_url,
        client_id=os.getenv('AZURE_APPLICATION_CLIENT_ID', default=None)
    )
