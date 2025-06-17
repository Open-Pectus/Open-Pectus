import json
import logging
import os
from pathlib import Path

import httpx
import openpectus.aggregator.deps as agg_deps
import openpectus.aggregator.models as Mdl
import openpectus.aggregator.routers.dto as Dto
from fastapi import APIRouter, BackgroundTasks, Depends
from openpectus.aggregator.aggregator import Aggregator
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import WebPushRepository
from openpectus.aggregator.routers.auth import UserIdValue, UserRolesValue
from starlette.status import HTTP_410_GONE
from webpush import VAPID, WebPush, WebPushSubscription
from webpush.types import AnyHttpUrl, WebPushKeys

logger = logging.getLogger(__name__)
router = APIRouter(tags=["webpush"], prefix="/webpush")

try:
    webpush_keys_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "webpush_keys")
    private_key_path = os.path.join(webpush_keys_path, "private_key.pem")
    public_key_path = os.path.join(webpush_keys_path, "public_key.pem")
    app_server_key_path = os.path.join(webpush_keys_path, "applicationServerKey")
    try:
        private_key = open(private_key_path).readline()
        public_key = open(public_key_path).readline()
        app_server_key = open(app_server_key_path).readline()
    except OSError:
        [private_key, public_key, app_server_key] = VAPID.generate_keys()
        open(private_key_path, 'xb').write(private_key)
        open(public_key_path, 'xb').write(public_key)
        open(app_server_key_path, 'xt').write(app_server_key)
    wp = WebPush(
        private_key=Path(os.path.join(webpush_keys_path, "private_key.pem")),
        public_key=Path(os.path.join(webpush_keys_path, "public_key.pem")),
        subscriber="jhk@mjolner.dk",  # TODO: take from env variable
        ttl=30,
    )
except OSError:
    app_server_key = None
    wp = None


@router.get("/config")
def get_webpush_config() -> Dto.WebPushConfig:
    return Dto.WebPushConfig(
        app_server_key=app_server_key
    )


@router.get("/notification_preferences")
def get_notification_preferences(user_id_from_token: UserIdValue,
                                 user_roles: UserRolesValue,
                                 agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.WebPushNotificationPreferences:
    preferences = agg.from_frontend.webpush_notification_preferences_requested(user_id_from_token, user_roles)
    return Dto.WebPushNotificationPreferences(scope=preferences.scope, topics=preferences.topics, process_units=preferences.process_units)


@router.post('/notification_preferences')
def save_notification_preferences(notification_preferences: Dto.WebPushNotificationPreferences,
                                  user_id_from_token: UserIdValue,
                                  user_roles: UserRolesValue,
                                  agg: Aggregator = Depends(agg_deps.get_aggregator)):
    model = Mdl.WebPushNotificationPreferences(user_id=str(user_id_from_token),
                                               user_roles=user_roles,
                                               scope=notification_preferences.scope,
                                               topics=notification_preferences.topics,
                                               process_units=notification_preferences.process_units)
    agg.from_frontend.webpush_notification_preferences_posted(model)


@router.post("/subscribe")
def subscribe_user(subscription: WebPushSubscription,
                   user_id: UserIdValue,
                   agg: Aggregator = Depends(agg_deps.get_aggregator)):
    action_result = agg.from_frontend.webpush_user_subscribed(subscription, user_id)
    if not action_result:
        return Dto.ServerErrorResponse(message="Web push subscription failed")
    return Dto.ServerSuccessResponse(message="Web push subscription successful")


@router.post("/notify_user")
def notify_user(user_id_from_token: UserIdValue,
                background_tasks: BackgroundTasks):
    if wp == None:
        return

    with database.create_scope():
        webpush_repo = WebPushRepository(database.scoped_session())
        subscriptions = webpush_repo.get_subscriptions(str(user_id_from_token))
        logger.debug(f"Publishing to {len(subscriptions)} subscription(s) for user {user_id_from_token}")
        if (len(subscriptions) == 0):
            return Dto.ServerErrorResponse(message="No subscription found")
        for subscription in subscriptions:
            logger.debug(f"Publishing subscription with id {subscription.id} for user {user_id_from_token}")
            # Encrypt message before sending
            message = wp.get(
                message=json.dumps(dict(
                    notification=dict(
                        title="Something happened",
                        body="It's probably fine",
                        icon="/assets/icons/icon-192x192.png",
                        data=dict(
                            id="<some id>"
                        ),
                        actions=list([
                            dict(
                                action="navigate",
                                title="Go to process unit"
                            )
                        ])
                    )
                )),
                subscription=WebPushSubscription(endpoint=AnyHttpUrl(subscription.endpoint),
                                                 keys=WebPushKeys(auth=subscription.auth, p256dh=subscription.p256dh)),
            )
            # Publish message to notification endpoint
            # background_tasks.add_task(
            #     httpx.post,
            #     url=subscription.endpoint,
            #     content=message.encrypted,
            #     headers=message.headers,  # type: ignore
            # )
            response = httpx.post(
                url=str(subscription.endpoint),
                content=message.encrypted,
                headers=message.headers  # pyright: ignore [reportArgumentType]
            )
            if (response.status_code == HTTP_410_GONE):
                webpush_repo.delete_subscription(subscription)
        return Dto.ServerSuccessResponse(message="Web push notification successful")
