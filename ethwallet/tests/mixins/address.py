__author__ = 'andrew.shvv@gmail.com'

from rest_framework import status

from core.utils.logging import getLogger

logger = getLogger(__name__)


class AddressMixin():
    def create_address(self, with_checks=True, user=None, debug=False):
        if user:
            # Authenticate normal user
            self.client.force_authenticate(user)

        # Create account
        response = self.client.post('/v1/addresses/', format='json')
        if debug:
            logger.debug(response.content)

        if with_checks:
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        return response.json()

    def send_eth(self, amount, address, user=None, debug=False, with_checks=True):
        if user:
            # Authenticate normal user
            self.client.force_authenticate(user)

        data = {
            "address": address,
            "amount": str(amount)
        }

        response = self.client.post('/v1/send/', format='json', data=data)

        if debug:
            logger.debug(response.content)

        if with_checks:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
