from mock import patch, MagicMock

from core.utils.logging import getLogger

__author__ = 'andrew.shvv@gmail.com'

logger = getLogger(__name__)

notifications = []


class NotificationMockMixin():
    """
        NotificationMockMixin substitute original 'notify_user' celery task.
    """

    def __init__(self):
        # WARNING!: Be careful with names you may override variables in the class that inherit this mixin!
        self._notify_patcher = None

    def get_notifications(self, url=None):
        global notifications
        return notifications

    def notification_flush(self):
        global notifications
        notifications = []

    def mock_notification(self):
        mock = MagicMock(return_value=MockClient())
        self._notify_patcher = patch('ethwallet.notifications.NotifyClient', new=mock)
        self._notify_patcher.start()

    def unmock_notification(self):
        self._notify_patcher.stop()


class MockClient():
    def notify(self, *args, **kwargs):
        global notifications
        notifications.append({
            'func': "notify",
            'args': args,
            'kwargs': kwargs
        })
