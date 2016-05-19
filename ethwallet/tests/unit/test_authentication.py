__author__ = 'andrew.shvv@gmail.com'

import hashlib
import hmac
import time
from random import choice
from string import printable

from rest_framework.test import APIClient


def add_auth_info(func):
    def decorator(self, *args, **kwargs):
        check_data = "".join([choice(printable) for _ in range(50)])
        signature = hmac.new(self.api_secret.encode(), check_data.encode(), hashlib.sha256).hexdigest()
        timestamp = str(int(time.time()))

        kwargs['ETHWALLET-VERSION'] = "1.0"
        kwargs['ETHWALLET-ACCESS-KEY'] = self.api_key
        kwargs['ETHWALLET-ACCESS-SIGN'] = signature
        kwargs['ETHWALLET-ACCESS-CHECKDATA'] = check_data
        kwargs['ETHWALLET-ACCESS-TIMESTAMP'] = timestamp

        request = func(self, *args, **kwargs)

        print(request)
        return request

    return decorator


class HMACClient(APIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_secret = None
        self.api_key = None

    def init_user(self, user):
        self.api_secret = user.api_secret
        self.api_key = user.api_key

    def credentials(self, **kwargs):
        print("KWARGS:".format(kwargs))
        super().credentials(**kwargs)

    def request(self, **kwargs):
        request = super().request(**kwargs)
        print("REQUEST: {}".format(request))
        return request

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
