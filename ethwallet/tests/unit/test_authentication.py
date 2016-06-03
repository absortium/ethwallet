import json

__author__ = 'andrew.shvv@gmail.com'

import hashlib
import hmac
import time

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ethwallet.models import Address

from ethwallet.tests.base import EthWalletUnitTest
from core.utils.logging import getLogger

logger = getLogger(__name__)


class AuthenticationTest(EthWalletUnitTest):
    def test_authentication(self):
        User = get_user_model()
        user = User(username="n87gvYb0u76G")
        user.save()

        self.client.logout()
        self.client = HMACClient()
        self.client.init_user(user)

        first_address = self.create_address()
        obj = Address.objects.get(pk=first_address['pk'])
        self.assertEqual(obj.owner, user)

        second_address = self.create_address()
        obj = Address.objects.get(pk=second_address['pk'])
        self.assertEqual(obj.owner, user)

        self.send_eth(from_address=first_address['address'],
                      to_address=second_address['address'],
                      amount=1,
                      debug=True)


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
