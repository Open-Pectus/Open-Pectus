import json
import logging

import openpectus.aggregator.deps as agg_deps
import openpectus.aggregator.models as Mdl
import openpectus.aggregator.routers.dto as Dto
from fastapi import APIRouter, Depends, HTTPException
from openpectus.aggregator.aggregator import Aggregator
from openpectus.aggregator.routers.auth import UserIdValue, UserRolesValue
from starlette.status import HTTP_404_NOT_FOUND
from webpush import WebPushSubscription

logger = logging.getLogger(__name__)
router = APIRouter(tags=["webpush"], prefix="/webpush")



@router.get("/config")
def get_webpush_config(agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.WebPushConfig:
    return Dto.WebPushConfig(
        app_server_key=agg.webpush_publisher.app_server_key
    )


@router.get("/notification_preferences")
def get_notification_preferences(user_id_from_token: UserIdValue,
                                 user_roles: UserRolesValue,
                                 agg: Aggregator = Depends(agg_deps.get_aggregator)) -> Dto.WebPushNotificationPreferences:
    preferences = agg.from_frontend.webpush_notification_preferences_requested(user_id_from_token, user_roles)
    return Dto.WebPushNotificationPreferences(scope=preferences.scope, topics=list(preferences.topics), process_units=list(preferences.process_units))


@router.post('/notification_preferences')
def save_notification_preferences(notification_preferences: Dto.WebPushNotificationPreferences,
                                  user_id_from_token: UserIdValue,
                                  user_roles: UserRolesValue,
                                  agg: Aggregator = Depends(agg_deps.get_aggregator)):
    model = Mdl.WebPushNotificationPreferences(user_id=str(user_id_from_token),
                                               user_roles=user_roles,
                                               scope=notification_preferences.scope,
                                               topics=set(notification_preferences.topics),
                                               process_units=set(notification_preferences.process_units))
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
def notify_user(process_unit_id: str,
                agg: Aggregator = Depends(agg_deps.get_aggregator)):
    message = Mdl.WebPushNotification(
        title="Something happened",
        body="It's probably fine",
        icon="/assets/icons/icon-192x192.png",
        data=Mdl.WebPushData(
            process_unit_id=process_unit_id
        ),
        actions=list([
            Mdl.WebPushAction(
                action="navigate",
                title="Go to process unit"
            )
        ])
    )

    engine_data = agg.get_registered_engine_data(process_unit_id)
    if(engine_data == None):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    agg.webpush_publisher.publish_message(message, Mdl.NotificationTopic.BLOCK_START, engine_data)
    return Dto.ServerSuccessResponse(message="Web push notification successful")
