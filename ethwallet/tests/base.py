__author__ = 'andrew.shvv@gmail.com'

import time

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase, APIClient, APITransactionTestCase

from core.utils.logging import getLogger
from ethwallet import celery_app
from ethwallet.tests.mixins.address import AddressMixin
from ethwallet.tests.mixins.notification import NotificationMockMixin
from ethwallet.tests.mixins.rpcclient import RPCClientMockMixin

logger = getLogger(__name__)


class EthWalletTestMixin():
    def get_first(self, response):
        self.assertEqual(response.status_code, HTTP_200_OK)

        json = response.json()
        results = json['results']

        self.assertGreaterEqual(len(results), 0)

        return results[0]


class EthWalletLiveTest(APITransactionTestCase,
                        AddressMixin,
                        EthWalletTestMixin):
    def setUp(self):
        super().setUp()

        User = get_user_model()
        user = User(username="primary", password="test", web_hook="www.somewebhook.com")
        user.save()

        self.user = user
        self.client = APIClient()
        self.client.force_authenticate(self.user)

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
                        AddressMixin,
                        RPCClientMockMixin,
                        NotificationMockMixin):
    def setUp(self):
        super().setUp()
        self.mock_rpcclient()
        self.mock_notification()

        User = get_user_model()
        user = User(username="primary", password="test", web_hook="www.somewebhook.com")
        user.save()

        self.user = user
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tearDown(self):
        self.unmock_rpcclient()
        self.unmock_notification()
        super().tearDown()
