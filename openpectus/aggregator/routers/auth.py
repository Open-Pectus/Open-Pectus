import os

from fastapi import APIRouter
from openpectus.aggregator.routers.dto import AuthConfig

router = APIRouter(tags=['auth'])


@router.get('/config')
def get_config() -> AuthConfig:
    tenant_id = os.getenv('AZURE_DIRECTORY_TENANT_ID', default=None)
    authority_url = f'https://login.microsoftonline.com/{tenant_id}/v2.0' if tenant_id else None
    return AuthConfig(
        use_auth=os.getenv('ENABLE_AZURE_AUTHENTICATION', default='').lower() == 'true',
        authority_url=authority_url,
        client_id=os.getenv('AZURE_APPLICATION_CLIENT_ID', default=None)
    )
