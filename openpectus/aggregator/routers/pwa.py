from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Header

from openpectus.aggregator.routers.dto import PWA, PWAIcon, PWAShortcut

router = APIRouter(tags=["pwa"], include_in_schema=False)

@router.get("/app.webmanifest")
def get_config(host: Annotated[str, Header()]) -> PWA:
    id = host if host else "openpectus"
    icons = [
        PWAIcon(
            src="/assets/icons/192.png",
            type="image/png",
            sizes="192x192",
        ),
        PWAIcon(
            src="/assets/icons/384.png",
            type="image/png",
            sizes="384x384",
        ),
        PWAIcon(
            src="/assets/icons/512.png",
            type="image/png",
            sizes="512x512",
        ),
        PWAIcon(
            src="/assets/icons/1024.png",
            type="image/png",
            sizes="1024x1024",
        ),
    ]
    
    shortcuts = [
        PWAShortcut(
            name="Process Unit Dashboard",
            short_name="Dashboard",
            url="/dashboard",
            icons=icons,
        )
    ]

    return PWA(
        id=id,
        name="Open Pectus",
        short_name="Open Pectus",  # ~12 character limit on short_name is OK
        icons=icons,
        start_url="/",
        display="standalone",
        description="Open Pectus is a process control system. Documentation is available at https://docs.openpectus.org. Source code is available at https://github.com/Open-Pectus/Open-Pectus.",
        categories=["productivity"],
        lang="en",
        dir="ltr",
        orientation="any",
        background_color="#FFFFFF",
        scope="/",
        shortcuts=shortcuts,
    )