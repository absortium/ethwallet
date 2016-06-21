from mock import patch, MagicMock

from core.utils.logging import getLogger

__author__ = 'andrew.shvv@gmail.com'

logger = getLogger(__name__)

_notifications = {}


class NotificationMockMixin():
    """
        NotificationMockMixin substitute original 'notify_user' celery task.
    """

    def __init__(self):
        # WARNING!: Be careful with names you may override variables in the class that inherit this mixin!
        self._notify_patcher = None

    def get_notifications(self, url=None):
        global _notifications

        if url is None:
            return _notifications
        else:
            try:
                return _notifications[url]
            except KeyError:
                return None

    def notification_flush(self):
        global _notifications
        _notifications = {}

    def mock_notification(self):
        mock = MagicMock(return_value=MockClient())
        self._notify_patcher = patch('ethwallet.notifications.NotifyClient', new=mock)
        self._notify_patcher.start()

    def unmock_notification(self):
        self._notify_patcher.stop()


class MockClient():
    def notify(self, webhook, address, tx_hash, value):
        global _notifications
        _notifications.setdefault(webhook, {}).setdefault(address, []).append((tx_hash, value))
