from ethwallet import notifications
from ethwallet.notifications import get_notify_client
from ethwallet.tests.base import EthWalletUnitTest

__author__ = 'andrew.shvv@gmail.com'


class NotificationsTest(EthWalletUnitTest):
    def test_notification_atomic_with_exception(self):
        """
            Check notifications.atomic context manager. If exception was raised inside the block
            than notification should not be published.
        """

        try:
            with notifications.atomic():
                client = get_notify_client()
                client.notify(webhook="somewebhook", address="address", tx_hash="hash", value="1")
                raise Exception("Something wrong! Bam!")
        except Exception:
            self.assertEqual(self.get_notifications("somewebhook"), None)

    def test_notification_atomic_without_exception(self):
        """
            Check notifications.atomic context manager. If exception was raised inside the block
            than notification should not be published.
        """

        with notifications.atomic():
            client = get_notify_client()
            client.notify(webhook="somewebhook", address="address", tx_hash="hash", value="1")
            self.assertEqual(self.get_notifications("somewebhook"), None)

        self.assertNotEqual(self.get_notifications("somewebhook"), None)
