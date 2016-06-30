from core.utils.logging import getPrettyLogger

__author__ = 'andrew.shvv@gmail.com'
logger = getPrettyLogger(__name__)

_client = None


def get_notify_client():
    global _client
    if _client is None:
        _client = NotifyClient()
    return _client


def set_notify_client(client):
    global _client
    _client = client


class NotifyClient():
    def notify(self, *args, **kwargs):
        from ethwallet.celery import tasks
        tasks.notify_user.delay(*args, **kwargs)


class atomic:
    """
        This class is used for notifying user about arriving transaction if no exceptions was raised.
    """

    client = None
    notifications = None

    def __enter__(self):
        self.notifications = []
        self.client = get_notify_client()

        set_notify_client(self)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            for notification in self.notifications:
                args = notification['args']
                kwargs = notification['kwargs']
                
                self.client.notify(*args, **kwargs)

        set_notify_client(self.client)

    def notify(self, *args, **kwargs):
        self.notifications.append({'args': args, 'kwargs': kwargs})
