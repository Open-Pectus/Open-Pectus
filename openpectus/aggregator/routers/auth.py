import os
import jwt

from typing import Annotated
from fastapi import APIRouter, security, Security, HTTPException, status
from openpectus.aggregator.routers.dto import AuthConfig

router = APIRouter(tags=['auth'])

# much in this file is based on https://alukach.com/posts/fastapi-rs256-jwt/

use_auth = os.getenv('ENABLE_AZURE_AUTHENTICATION', default='').lower() == 'true'
tenant_id = os.getenv('AZURE_DIRECTORY_TENANT_ID', default=None)
authority_url = f'https://login.microsoftonline.com/{tenant_id}/v2.0' if tenant_id else None
client_id = os.getenv('AZURE_APPLICATION_CLIENT_ID', default=None)
token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'
authorization_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/authorize'
jwks_url = 'https://login.microsoftonline.com/common/discovery/keys'


@router.get('/config')
def get_config() -> AuthConfig:
    return AuthConfig(
        use_auth=use_auth,
        authority_url=authority_url,
        client_id=client_id
    )

oauth2_scheme = security.OAuth2AuthorizationCodeBearer(
    authorizationUrl=authorization_url,
    tokenUrl=token_url,
)
jwks_client = jwt.PyJWKClient(jwks_url)

def access_token(token_str: Annotated[str, Security(oauth2_scheme)]):
    if(not use_auth): return None
    try:
        token = jwt.decode(
            token_str,
            jwks_client.get_signing_key_from_jwt(token_str).key,
            algorithms=["RS256"],
            audience=['00000003-0000-0000-c000-000000000000'] # Microsoft Graph https://learn.microsoft.com/en-us/troubleshoot/entra/entra-id/governance/verify-first-party-apps-sign-in#application-ids-of-commonly-used-microsoft-applications
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


    return token
