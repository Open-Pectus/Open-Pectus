import json
import logging
import os

import httpx
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import WebPushRepository
from openpectus.aggregator.models import WebPushNotification
from starlette.status import HTTP_410_GONE
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

    def publish_message(self, notification: WebPushNotification, user_id: str | None):
        if (self.wp == None): return

        with database.create_scope():
            webpush_repo = WebPushRepository(database.scoped_session())
            subscriptions = webpush_repo.get_subscriptions(str(user_id))
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
