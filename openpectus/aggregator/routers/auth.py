import os
import jwt

from typing import Annotated
from fastapi import APIRouter, security, Security, HTTPException, status
from fastapi.params import Header
from openpectus.aggregator.routers.dto import AuthConfig

router = APIRouter(tags=['auth'])

# much in this file is based on https://alukach.com/posts/fastapi-rs256-jwt/

use_auth = os.getenv('ENABLE_AZURE_AUTHENTICATION', default='').lower() == 'true'
tenant_id = os.getenv('AZURE_DIRECTORY_TENANT_ID', default=None)
authority_url = f'https://login.microsoftonline.com/{tenant_id}/v2.0' if tenant_id else None
client_id = os.getenv('AZURE_APPLICATION_CLIENT_ID', default=None)
# token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'
# authorization_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/authorize'
jwks_url = 'https://login.microsoftonline.com/common/discovery/keys'


@router.get('/config')
def get_config() -> AuthConfig:
    return AuthConfig(
        use_auth=use_auth,
        authority_url=authority_url,
        client_id=client_id
    )

# oauth2_scheme = security.OAuth2AuthorizationCodeBearer(
#     authorizationUrl=authorization_url,
#     tokenUrl=token_url,
# )

jwks_client = jwt.PyJWKClient(jwks_url)

def user_roles(x_identity: Annotated[str, Header()]):
    if(not use_auth): return None
    try:
        token: dict = jwt.decode(
            x_identity,
            jwks_client.get_signing_key_from_jwt(x_identity).key,
            algorithms=["RS256"],
            audience=client_id,
            issuer=authority_url
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate id token in X-Identity header",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    return token.get('roles') or []
