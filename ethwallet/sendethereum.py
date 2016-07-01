from core.utils.logging import getPrettyLogger

__author__ = 'andrew.shvv@gmail.com'
logger = getPrettyLogger(__name__)

client = None


def get_send_client():
    global client
    if client is None:
        client = SendClient()
    return client


def set_send_client(c):
    global client
    client = c


class SendClient():
    def send(self, *args, **kwargs):
        from ethwallet.celery import tasks
        tasks.send.delay(*args, **kwargs)


class atomic:
    """
        This class is used for send etheherum to user only if no exceptions was raised.
    """

    client = None
    operations = None

    def __enter__(self):
        self.operations = []
        self.client = get_send_client()

        set_send_client(self)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_val:
            for operation in self.operations:
                args = operation['args']
                kwargs = operation['kwargs']

                self.client.send(*args, **kwargs)

        set_send_client(self.client)

    def send(self, *args, **kwargs):
        self.operations.append({'args': args, 'kwargs': kwargs})
