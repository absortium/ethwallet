from ethwallet.models import Address

__author__ = 'andrew.shvv@gmail.com'

from core.utils.logging import getLogger
from ethwallet.tests.base import EthWalletUnitTest

logger = getLogger(__name__)


class UserTest(EthWalletUnitTest):
    def test_creation(self):
        self.assertEqual(len(Address.objects.filter(base_address=True, owner_id=self.user.pk)), 1)
