__author__ = 'andrew.shvv@gmail.com'

from django.contrib.auth import get_user_model
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED

from core.utils.logging import getLogger
from ethwallet.models import Address
from ethwallet.tests.base import EthWalletUnitTest

logger = getLogger(__name__)


class AddressTest(EthWalletUnitTest):
    def test_creation_mixin(self):
        address = self.create_address()

        obj = Address.objects.get(pk=address['pk'])
        self.assertEqual(obj.owner_id, self.user.pk)

    def test_permissions(self, *args, **kwargs):
        address = self.create_address()

        # User trying to delete address
        url = '/v1/addresses/{pk}/'.format(pk=address['pk'])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, HTTP_405_METHOD_NOT_ALLOWED)

        # Create hacker user
        User = get_user_model()
        hacker = User(username="hacker")
        hacker.save()

        # Authenticate hacker
        self.client.force_authenticate(hacker)

        # Hacker trying access info of normal user address
        url = '/v1/addresses/{pk}/'.format(pk=address['pk'])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_malformed(self):
        trash_address_pk = "19087698021"

        # User trying to delete not created address
        url = '/v1/addresses/{pk}/'.format(pk=trash_address_pk)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, HTTP_405_METHOD_NOT_ALLOWED)

        # User trying to get not created account
        url = '/v1/addresses/{pk}/'.format(pk=trash_address_pk)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
