import os
from typing import Annotated, Any

import jwt
from openpectus.aggregator.data.models import RecentEngine, RecentRun
from openpectus.aggregator.models import EngineData
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Header, Security
from openpectus.aggregator.routers.dto import AuthConfig

router = APIRouter(tags=['auth'])

# much in this file is based on https://alukach.com/posts/fastapi-rs256-jwt/

use_auth = os.getenv('ENABLE_AZURE_AUTHENTICATION', default='').lower() == 'true'
tenant_id = os.getenv('AZURE_DIRECTORY_TENANT_ID', default=None)
authority_url = f'https://login.microsoftonline.com/{tenant_id}/v2.0' if tenant_id else None
well_known_url = f'{authority_url}/.well-known/openid-configuration' if authority_url else None
client_id = os.getenv('AZURE_APPLICATION_CLIENT_ID', default=None)
# token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'
# authorization_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/authorize'
jwks_url = 'https://login.microsoftonline.com/common/discovery/keys'

if use_auth:
    print("Authentication enabled")
else:
    print("Authentication disabled")


@router.get('/config')
def get_config() -> AuthConfig:
    return AuthConfig(
        use_auth=use_auth,
        authority_url=authority_url,
        client_id=client_id,
        well_known_url=well_known_url
    )

# oauth2_scheme = security.OAuth2AuthorizationCodeBearer(
#     authorizationUrl=authorization_url,
#     tokenUrl=token_url,
# )


jwks_client = jwt.PyJWKClient(jwks_url)

def decode_token_or_fail(x_identity) -> dict[str, Any]:
    try:
        token: dict[str, str | list[str]] = jwt.decode(
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
    return token


def user_name(x_identity: Annotated[str, Header()] = '') -> str:
    if not use_auth:
        return "Anon"

    token = decode_token_or_fail(x_identity)
    preferred_username = token.get("preferred_username", "")  # email address, field 'name' has full name
    if "@" in preferred_username:
        preferred_username = preferred_username[0: preferred_username.index("@")]
    return str(preferred_username).upper()


def user_roles(x_identity: Annotated[str, Header()] = '') -> set[str]:
    if not use_auth:
        return set()

    token = decode_token_or_fail(x_identity)
    return set(token.get('roles') or [])


UserRolesDependency = Security(user_roles)
UserRolesValue = Annotated[set[str], UserRolesDependency]
UserNameDependency = Security(user_name)
UserNameValue = Annotated[str, UserNameDependency]


def has_access(engine_or_run: EngineData | RecentEngine | RecentRun, user_roles: set[str]):
    required_roles = set(engine_or_run.required_roles)
    return len(required_roles) == 0 or len(required_roles & user_roles) > 0
