from ethwallet.utils import HMACClient

__author__ = 'andrew.shvv@gmail.com'

from django.contrib.auth import get_user_model

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
        obj = Address.objects.get(address=first_address['address'])
        self.assertEqual(obj.owner, user)

        second_address = self.create_address()
        obj = Address.objects.get(address=second_address['address'])
        self.assertEqual(obj.owner, user)
