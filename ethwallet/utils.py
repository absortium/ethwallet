import binascii
import hashlib
import hmac
import json
import os
import time
from decimal import Decimal, localcontext, ROUND_DOWN
from random import choice
from string import printable

import math
from django.conf import settings
from rest_framework.test import APIClient

from core.utils.logging import getPrettyLogger
from ethwallet import constants

logger = getPrettyLogger(__name__)

__author__ = 'andrew.shvv@gmail.com'


def random_string(length=30):
    return "".join([choice(printable) for _ in range(length)])


def generate_token(length=128):
    return hashlib.sha1(os.urandom(length)).hexdigest()


def get_wallet_password(key):
    if type(key) is not bytes:
        key = key.encode()

    salt = settings.SECRET_KEY.encode()
    dk = hashlib.pbkdf2_hmac('sha256', password=key, salt=salt, iterations=constants.PASSWORD_ITERATIONS)

    return binascii.hexlify(dk).decode()


def add_auth_info(func):
    def decorator(self, *args, **kwargs):
        data = kwargs.get('data')
        if data:
            message = json.dumps(data, separators=(',', ':'))
        else:
            message = ''

        signature = hmac.new(self.api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
        timestamp = str(int(time.time()))

        kwargs['HTTP_ETHWALLET_VERSION'] = "1.0"
        kwargs['HTTP_ETHWALLET_ACCESS_KEY'] = self.api_key
        kwargs['HTTP_ETHWALLET_ACCESS_SIGN'] = signature
        kwargs['HTTP_ETHWALLET_ACCESS_TIMESTAMP'] = timestamp

        request = func(self, *args, **kwargs)
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
        super().credentials(**kwargs)

    def request(self, **kwargs):
        request = super().request(**kwargs)
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


def wei2eth(value):
    return truncate(Decimal(value) / constants.WEI_INT_ETH, constants.DECIMAL_PLACES)


def eth2wei(value):
    return int(Decimal(value) * constants.WEI_INT_ETH)


def register(operations, debug=False):
    def wrapper(func):
        def decorator(*args, **kwargs):
            operation = {
                'func': func.__name__,
                'args': args,
                'kwargs': kwargs
            }

            if debug:
                logger.debug(operation)

            operations.append(operation)

            return func(*args, **kwargs)

        return decorator

    return wrapper


def truncate(number, places):
    if not isinstance(places, int):
        raise ValueError("Decimal places must be an integer.")
    if places < 1:
        raise ValueError("Decimal places must be at least 1.")
    # If you want to truncate to 0 decimal places, just do int(number).

    with localcontext() as context:
        context.rounding = ROUND_DOWN
        exponent = Decimal(str(math.pow(10, - places)))
        return Decimal(str(number)).quantize(exponent)
