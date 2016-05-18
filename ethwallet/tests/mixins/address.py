__author__ = 'andrew.shvv@gmail.com'

from rest_framework.status import HTTP_201_CREATED

from core.utils.logging import getLogger

logger = getLogger(__name__)


class CreateAddressMixin():
    def create_address(self, with_checks=True, user=None, debug=False):
        if user:
            # Authenticate normal user
            self.client.init_user(user)

        # Create account
        response = self.client.post('/addresses/', format='json')
        if debug:
            logger.debug(response.content)

        if with_checks:
            self.assertEqual(response.status_code, HTTP_201_CREATED)

        return response.json()
