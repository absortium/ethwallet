from mock import patch, Mock

from core.utils.logging import getLogger

__author__ = 'andrew.shvv@gmail.com'

logger = getLogger(__name__)

_notifications = None


class NotificationMockMixin():
    """
        EthnodeMockMixin substitute original rpc client and return mock block information.
    """

    def __init__(self):
        # WARNING!: Be careful with names you may override variables in the class that inherit this mixin!
        self._notify_patcher = None

    def get_notification(self):
        global _notifications
        return _notifications

    def mock_notification(self):
        global _notifications
        _notifications = {}

        self._notify_patcher = patch('ethwallet.celery.tasks.notify_user', new=Mock(delay=mock_notify_user))
        self._notify_patcher.start()

    def unmock_notification(self):
        self._notify_patcher.stop()


def mock_notify_user(webhook, address, tx_hash, value):
    global _notifications
    _notifications.setdefault(webhook, {}).setdefault(address, []).append((tx_hash, value))
