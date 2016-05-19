__author__ = 'andrew.shvv@gmail.com'


class NotificationClient():
    """
        This class is used for user notification about arriving transaction only if no exceptions was raised.
        You can turn off this behaviour by setting atomic=False
    """

    def __init__(self, atomic=True):
        # I know that is kind of tricky but otherwise NotificationMockMixin is not working.
        from ethwallet.celery.tasks import notify_user
        self.func = notify_user

        self.atomic = atomic
        self.notifications = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_val and self.atomic:
            for notification in self.notifications:
                args = notification['args']
                kwargs = notification['kwargs']

                self.func.delay(*args, **kwargs)

    def notify(self, *args, **kwargs):
        if self.atomic:
            self.notifications.append({'args': args, 'kwargs': kwargs})
        else:
            self.func.delay(*args, **kwargs)
