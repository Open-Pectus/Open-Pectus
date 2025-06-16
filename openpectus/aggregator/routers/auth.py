import os
import uuid
from typing import Annotated, Any

import jwt
from openpectus.aggregator.data.models import RecentEngine, RecentRun
from openpectus.aggregator.models import EngineData
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Header, Security
from openpectus.aggregator.routers.dto import AuthConfig

router = APIRouter(tags=["auth"])

# Much in this file is based on https://alukach.com/posts/fastapi-rs256-jwt/
# Authentication is possible via PKCE flow or via client secret for daemon
# applications.
# Remember to add optional claim "idtyp" on Azure App Registration -> Token configuration page.

use_auth = os.getenv("ENABLE_AZURE_AUTHENTICATION", default="").lower() == "true"
tenant_id = os.getenv("AZURE_DIRECTORY_TENANT_ID", default=None)
client_id = os.getenv("AZURE_APPLICATION_CLIENT_ID", default=None)
authority_url = f"https://login.microsoftonline.com/{tenant_id}/v2.0" if tenant_id else None
well_known_url = f"{authority_url}/.well-known/openid-configuration" if tenant_id else None
jwks_url_id_token = "https://login.microsoftonline.com/common/discovery/keys"
jwks_url_access_token = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys" if tenant_id else ""
access_token_issuer = f"https://sts.windows.net/{tenant_id}/" if tenant_id else ""

if use_auth:
    assert tenant_id is not None, "Assign Tenant ID to environment variable AZURE_DIRECTORY_TENANT_ID"
    assert client_id is not None, "Assign Client ID to environment variable AZURE_APPLICATION_CLIENT_ID"

@router.get("/config")
def get_config() -> AuthConfig:
    return AuthConfig(
        use_auth=use_auth,
        authority_url=authority_url,
        client_id=client_id,
        well_known_url=well_known_url
    )


# PKCE and client secret flows use different keys:
jwks_client_pkce = jwt.PyJWKClient(jwks_url_id_token)
jwks_client_secret = jwt.PyJWKClient(jwks_url_access_token)


def decode_token_or_fail(x_identity) -> dict[str, Any]:
    # Bearer tokens from PKCE flow result in an ID token.
    # Bearer tokens from secret flow result in access token.
    # Try to parse either one. Raise exception if neither
    # can be validated.
    try:
        id_token: dict[str, str | list[str]] = jwt.decode(
            x_identity,
            jwks_client_pkce.get_signing_key_from_jwt(x_identity).key,
            algorithms=["RS256"],
            audience=client_id,
            issuer=authority_url
        )
        return id_token
    except jwt.PyJWTError:
        pass

    try:
        access_token: dict[str, str | list[str]] = jwt.decode(
            x_identity,
            jwks_client_secret.get_signing_key_from_jwt(x_identity),
            algorithms=["RS256"],
            audience=client_id,
            issuer=access_token_issuer
        )
        return access_token
    except jwt.PyJWTError:
        pass
    # If we got this far, then we couldn't validate the token in either case
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token in X-Identity header",
        headers={"WWW-Authenticate": "Bearer"},
    )


def user_name(x_identity: Annotated[str, Header()] = "") -> str:
    if not use_auth:
        return "Anon"

    token = decode_token_or_fail(x_identity)
    # Return default name "Daemon" for authenticated applications
    if token.get("idtyp", "") == "app":
        return "Daemon"
    preferred_username = token.get("preferred_username", "")  # email address, field 'name' has full name
    if "@" in preferred_username:
        preferred_username = preferred_username[0: preferred_username.index("@")]
    return str(preferred_username).upper()


def user_roles(x_identity: Annotated[str, Header()] = "") -> set[str]:
    if not use_auth:
        return set()

    token = decode_token_or_fail(x_identity)
    roles = set(token.get("roles") or [])
    # Add default role "Daemon" for authenticated applications
    if token.get("idtyp", "") == "app":
        roles |= set(["Daemon"])
    return roles

def user_id(x_identity: Annotated[str, Header()] = "") -> str | None:
    if not use_auth:
        return None

    token = decode_token_or_fail(x_identity)
    subject_id = token.get("oid", None)
    return subject_id


UserRolesDependency = Security(user_roles)
UserRolesValue = Annotated[set[str], UserRolesDependency]
UserNameDependency = Security(user_name)
UserNameValue = Annotated[str, UserNameDependency]
UserIdDependency = Security(user_id)
UserIdValue = Annotated[str | None, UserIdDependency]


def has_access(engine_or_run: EngineData | RecentEngine | RecentRun, user_roles: set[str]):
    required_roles = set(engine_or_run.required_roles)
    return len(required_roles) == 0 or len(required_roles & user_roles) > 0
