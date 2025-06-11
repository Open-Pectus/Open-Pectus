import logging
import os
from pathlib import Path
import uuid

import openpectus.aggregator.deps as agg_deps
import openpectus.aggregator.routers.dto as Dto
from fastapi import APIRouter, Depends
from pydantic.json_schema import SkipJsonSchema
from webpush import WebPush, WebPushSubscription
from openpectus.aggregator.aggregator import Aggregator
from openpectus.aggregator.routers.auth import UserIdValue, UserRolesValue


logger = logging.getLogger(__name__)
router = APIRouter(tags=["webpush"])

try:
    webpush_keys_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "webpush_keys")
    app_server_key_path = os.path.join(webpush_keys_path, "applicationServerKey")
    with open(app_server_key_path) as app_server_key_file:
        app_server_key = app_server_key_file.readline()
    wp = WebPush(
        private_key=Path(os.path.join(webpush_keys_path, "private_key.pem")),
        public_key=Path(os.path.join(webpush_keys_path, "public_key.pem")),
        # subscriber="", # TODO: take from env variable
        ttl=30,
    )
except OSError:
    app_server_key = None
    wp = None


@router.get("/config")
def get_webpush_config() -> Dto.WebPushConfig:
    return Dto.WebPushConfig(
        enabled = app_server_key != None,
        app_server_key = app_server_key
    )

@router.post("/subscribe")
async def subscribe_user(subscription: WebPushSubscription,
                         user_id_from_token: UserIdValue,
                         user_roles: UserRolesValue,
                         user_id: str | SkipJsonSchema[None] = None,
                         agg: Aggregator = Depends(agg_deps.get_aggregator)):
    resolved_user_id = user_id_from_token or user_id
    if(resolved_user_id == None):
        return Dto.ServerErrorResponse(message="Web push subscription failed due to missing user_id")
    action_result = agg.from_frontend.webpush_user_subscribed(subscription, uuid.UUID(resolved_user_id), user_id_from_token == None, user_roles)
    if not action_result:
        return Dto.ServerErrorResponse(message="Web push subscription failed")
    return Dto.ServerSuccessResponse(message="Web push subscription successful")
