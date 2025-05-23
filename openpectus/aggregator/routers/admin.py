import os
import re
import secrets
from typing import Optional

import identity.web
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin import BaseAdmin
from starlette_admin.auth import (
    AdminUser,
    AuthProvider,
    login_not_required,
)
from starlette_admin.contrib.sqla import Admin, ModelView

import openpectus
from openpectus.aggregator.data.models import (
    RecentEngine,
    RecentRun,
    RecentRunMethodAndState,
    RecentRunRunLog,
    RecentRunErrorLog,
    RecentRunPlotConfiguration,
    PlotLogEntryValue,
    PlotLogEntry,
    PlotLog,
)


def get_auth(request: Request):
    return identity.web.Auth(
        session=request.session,
        authority=f"https://login.microsoftonline.com/{os.environ.get("AZURE_DIRECTORY_TENANT_ID")}",
        client_id=os.environ.get("AZURE_APPLICATION_CLIENT_ID"),
        client_credential=os.environ.get("AZURE_CLIENT_SECRET"),
    )

def get_initials(user: dict[str, str]):
    '''
    Extract user initials from the 'name' key.
    An alternative might be to recover the initials
    from the 'preferred_username' key.
    '''
    m = re.match(r"(?P<initials>.{2,4}) \((?P<name>.*?)\)", user["name"])
    if m:
        return m.groupdict()["initials"].upper()
    else:
        return user["name"]

class AzureAuthProvider(AuthProvider):
    async def is_authenticated(self, request: Request) -> bool:
        auth = get_auth(request)
        user = auth.get_user()
        return True if user and "Administrator" in user.get("roles", []) else False

    def get_admin_user(self, request: Request) -> Optional[AdminUser]:
        auth = get_auth(request)
        user = auth.get_user()
        return AdminUser(username=get_initials(user))

    async def render_login(self, request: Request, admin: BaseAdmin):
        auth = get_auth(request)
        login = auth.log_in(
            scopes=["User.Read"],
            redirect_uri=str(request.url_for(f"{admin.route_name}:msal_callback")),
            next_link=request.query_params.get("next", str(request.url_for(f"{admin.route_name}:index"))),
        )
        return RedirectResponse(login["auth_uri"])

    async def render_logout(self, request: Request, admin: BaseAdmin) -> Response:
        request.session.clear()
        return RedirectResponse(request.url_for(f"{admin.route_name}:index"))

    @login_not_required
    async def handle_auth_callback(self, request: Request):
        auth = get_auth(request)
        result = auth.complete_log_in(dict(request.query_params))
        if "error" in result:
            return Response("Login failed", status_code=500)
        user = auth.get_user()
        user_initials = get_initials(user)
        if "Administrator" not in user.get("roles", []):
            return Response(f"Unauthorized access. User '{user_initials}' is not assinged to the Administrator role.", status_code=403)

        request.session.pop("_token_cache", None)
        return RedirectResponse(result.get("next_link"))

    def setup_admin(self, admin: BaseAdmin):
        """
        Add authentication callback route
        """
        super().setup_admin(admin)
        admin.routes.append(
            Route(
                "/msal",
                self.handle_auth_callback,
                methods=["GET"],
                name="msal_callback",
            )
        )

def build_administration(engine):
    assert engine
    admin = Admin(
        engine,
        title="Administration Panel",
        auth_provider=AzureAuthProvider() if os.environ.get("ENABLE_AZURE_AUTHENTICATION", "") == "true" else None,
        middlewares=[Middleware(SessionMiddleware, secret_key=secrets.token_urlsafe())],
        debug="dev" in openpectus.__version__,
        )

    for model in [
        RecentEngine,
        RecentRun,
        RecentRunMethodAndState,
        RecentRunRunLog,
        RecentRunErrorLog,
        RecentRunPlotConfiguration,
        PlotLogEntryValue,
        PlotLogEntry,
        PlotLog]:
        admin.add_view(ModelView(model))
    return admin