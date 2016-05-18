import hashlib
import hmac

__author__ = 'andrew.shvv@gmail.com'

import time

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase

from core.utils.logging import getLogger
from ethwallet import celery_app
from ethwallet.tests.mixins.address import CreateAddressMixin
from ethwallet.tests.mixins.rpcclient import RPCClientMockMixin
from ethwallet.tests.mixins.notification import NotificationMockMixin

logger = getLogger(__name__)


def add_auth_info(func):
    def decorator(self, *args, **kwargs):
        message = kwargs.get('data')
        signature = hmac.new(self.api_secret.encode(), message, hashlib.sha256).hexdigest()
        timestamp = str(int(time.time()))

        kwargs['ETHWALLET-VERSION'] = "1.0"
        kwargs['ETHWALLET-ACCESS-KEY'] = self.api_key
        kwargs['ETHWALLET-ACCESS-SIGN'] = signature
        kwargs['ETHWALLET-ACCESS-TIMESTAMP'] = timestamp

        return func(self, *args, **kwargs)

    return decorator


class HMACClient(APIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_secret = None
        self.api_key = None

    def init_user(self, user):
        self.api_secret = user.api_secret
        self.api_key = user.api_key

    @add_auth_info
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)

    @add_auth_info
    def put(self, *args, **kwargs):
        return super().put(*args, **kwargs)

    @add_auth_info
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    @add_auth_info
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


class EthWalletTestMixin():
    def get_first(self, response):
        self.assertEqual(response.status_code, HTTP_200_OK)

        json = response.json()
        results = json['results']

        self.assertGreaterEqual(len(results), 0)

        return results[0]


class EthWalletLiveTest(APITransactionTestCase,
                        EthWalletTestMixin):
    def setUp(self):
        super().setUp()

        User = get_user_model()
        user = User(username="primary", password="test", webhook="www.somewebhook.com")
        user.save()

        self.user = user
        self.client = HMACClient()
        self.client.init_user(self.user)

    def wait_celery(self, tag=None):
        # WARNING: Sometime may skip the execution and I don't know why
        i = celery_app.control.inspect()

        def queue_not_empty():
            queues = i.active()

            if not queues:
                raise Exception("Celery was stopped!")

            queue_empty = True
            for name, tasks in queues.items():
                if tasks:
                    queue_empty = False

            if tag:
                logger.debug("Wait for '{}'...".format(tag, queue_empty))

            return not queue_empty

        # i.active() may return empty list but process is not over
        # so lets check several times :)

        times = 3
        while all([queue_not_empty() for _ in range(times)]):
            time.sleep(0.2)


@override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                   CELERY_ALWAYS_EAGER=True)
class EthWalletUnitTest(APITestCase,
                        EthWalletTestMixin,
                        CreateAddressMixin,
                        RPCClientMockMixin,
                        NotificationMockMixin):
    def setUp(self):
        super().setUp()
        self.mock_rpcclient()

        User = get_user_model()
        user = User(username="primary", password="test", webhook="www.somewebhook.com")
        user.save()

        self.user = user
        self.client = HMACClient()
        self.client.init_user(self.user)

    def tearDown(self):
        self.unmock_rpcclient()
        super().tearDown()
