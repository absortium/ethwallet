__author__ = 'andrew.shvv@gmail.com'

from rest_framework.status import HTTP_201_CREATED

from core.utils.logging import getLogger

logger = getLogger(__name__)


class AddressMixin():
    def create_address(self, with_checks=True, user=None, debug=False):
        if user:
            # Authenticate normal user
            self.client.force_authenticate(user)

        # Create account
        response = self.client.post('/addresses/', format='json')
        if debug:
            logger.debug(response.content)

        if with_checks:
            self.assertEqual(response.status_code, HTTP_201_CREATED)

        return response.json()

    def send_eth(self, amount, from_address, to_address, user=None, debug=False, with_checks=True):
        self.assertEqual(type(amount), int)

        if user:
            # Authenticate normal user
            self.client.force_authenticate(user)

        data = {
            "address": to_address,
            "amount": amount
        }

        url = '/addresses/{from_address}/send/'.format(from_address=from_address)
        response = self.client.post(url, format='json', data=data)

        if debug:
            logger.debug(response.content)

        if with_checks:
            self.assertEqual(response.status_code, HTTP_201_CREATED)

        return response.json()
