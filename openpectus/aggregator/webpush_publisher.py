import json
import logging
import os
from typing import Sequence

import httpx
import openpectus.aggregator.data.models as db_mdl
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import WebPushRepository
from openpectus.aggregator.models import EngineData, NotificationScope, NotificationTopic, WebPushNotification
from openpectus.aggregator.routers.auth import has_access
from starlette.status import HTTP_201_CREATED, HTTP_410_GONE
from webpush import VAPID, Path, WebPush
from webpush.types import AnyHttpUrl, WebPushKeys, WebPushSubscription

logger = logging.getLogger(__name__)


class WebPushPublisher:
    def __init__(self, webpush_keys_path: str):
        self.webpush_keys_path = webpush_keys_path
        self.setup_webpush()

    def setup_webpush(self):
        try:
            webpush_keys_path = self.webpush_keys_path
            private_key_path = os.path.join(webpush_keys_path, "private_key.pem")
            public_key_path = os.path.join(webpush_keys_path, "public_key.pem")
            app_server_key_path = os.path.join(webpush_keys_path, "applicationServerKey")
            try:
                private_key = open(private_key_path).readline()
                public_key = open(public_key_path).readline()
                self.app_server_key = open(app_server_key_path).readline()
            except OSError:
                [private_key, public_key, self.app_server_key] = VAPID.generate_keys()
                open(private_key_path, 'xb').write(private_key)
                open(public_key_path, 'xb').write(public_key)
                open(app_server_key_path, 'xt').write(self.app_server_key)

            webpush_subscriber_email = os.getenv('WEBPUSH_SUBSCRIBER_EMAIL')
            if (webpush_subscriber_email == None):
                logger.warning('Missing WEBPUSH_SUBSCRIBER_EMAIL environment variable. Webpush will not work.')
            else:
                self.wp = WebPush(
                    private_key=Path(os.path.join(webpush_keys_path, "private_key.pem")),
                    public_key=Path(os.path.join(webpush_keys_path, "public_key.pem")),
                    subscriber=webpush_subscriber_email,
                    ttl=30,
                )
        except OSError:
            self.app_server_key = None
            self.wp = None

    async def publish_message(self, notification: WebPushNotification, topic: NotificationTopic, process_unit: EngineData):
        if (self.wp == None): return
        with database.create_scope():
            webpush_repo = WebPushRepository(database.scoped_session())
            subscriptions = self._get_subscriptions_for_topic(topic, process_unit, webpush_repo)
            for subscription in subscriptions:
                web_push_subscription = WebPushSubscription(endpoint=AnyHttpUrl(subscription.endpoint),
                                                            keys=WebPushKeys(auth=subscription.auth, p256dh=subscription.p256dh))
                message_json = json.dumps(dict(notification=notification.model_dump()))
                encryptedMessage = self.wp.get(message=message_json, subscription=web_push_subscription)
                response = httpx.post(
                    url=str(subscription.endpoint),
                    content=encryptedMessage.encrypted,
                    headers=encryptedMessage.headers  # pyright: ignore [reportArgumentType]
                )
                if (response.status_code == HTTP_410_GONE):
                    webpush_repo.delete_subscription(subscription)
                if(response.status_code != HTTP_201_CREATED):
                    logger.warning(f"Tried publishing message for user {subscription.user_id} to endpoint {subscription.endpoint} but got response status {response.status_code}")

    def _get_subscriptions_for_topic(self, topic: NotificationTopic, process_unit: EngineData, webpush_repo: WebPushRepository) -> Sequence[db_mdl.WebPushSubscription]:
        notification_preferences = webpush_repo.get_notification_preferences_for_topic(topic)
        access = [np.user_id for np in notification_preferences
                  if np.scope == NotificationScope.PROCESS_UNITS_I_HAVE_ACCESS_TO
                  and has_access(process_unit, set(np.user_roles))]
        contributed = [np.user_id for np in notification_preferences
                       if np.scope == NotificationScope.PROCESS_UNITS_WITH_RUNS_IVE_CONTRIBUTED_TO
                       and has_access(process_unit, set(np.user_roles))
                       and len([contributor for contributor in process_unit.contributors if contributor.id == np.user_id]) > 0]
        specific = [np.user_id for np in notification_preferences
                    if np.scope == NotificationScope.SPECIFIC_PROCESS_UNITS
                    and has_access(process_unit, set(np.user_roles))
                    and process_unit.engine_id in np.process_units]

        return webpush_repo.get_subscriptions(access + contributed + specific)
