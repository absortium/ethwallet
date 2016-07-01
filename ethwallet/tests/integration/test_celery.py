import time
from django.contrib.auth import get_user_model

from ethwallet import constants
from ethwallet.utils import wei2eth, truncate

__author__ = 'andrew.shvv@gmail.com'

from django.conf import settings

from core.utils.logging import getLogger
from ethwallet.models import Address
from ethwallet.rpc.client import RPCClient
from ethwallet.rpc.interfaces import HTTPInterface
from ethwallet.tests.base import EthWalletLiveTest

logger = getLogger(__name__)


class AccuracyTest(EthWalletLiveTest):
    def setUp(self):
        super().setUp()

        self.rpc = RPCClient(HTTPInterface(host=settings.ETHNODE_URL))
        self.coinbase = self.rpc.eth_coinbase()

        # Make alias
        self.primary = self.user

        # Make coinbase address base address of the primary user.
        address = Address.objects.get(owner=self.primary, is_base_address=True)
        address.update(address=self.coinbase)

    def test_send_transactions(self, *args, **kwargs):
        """
            In order to execute this test celery worker should use django test db, for that you should set
            the CELERY_TEST=True environment variable in the worker(celery) service. See docker-compose.yml
        """

        # Create secondary user
        User = get_user_model()
        user = User(username="secondary",
                    web_hook="http://somewebhook.com",
                    wallet_secret_key="secret")
        self.secondary = user
        user.save()

        # Create secondary user address to which we will send ethereum
        self.client.force_authenticate(self.secondary)
        address = self.create_address()['address']

        # Auth as primary and send ethereum
        self.client.force_authenticate(self.primary)

        # Calculate the transaction amount
        amount = wei2eth(self.rpc.eth_getBalance(address=self.primary.base_address.address))
        self.send_eth(address=address, amount=amount)

        # Wait while blocks will be proceed by ethereum node
        time.sleep(30)

        secondary_balance = self.rpc.eth_getBalance(address=self.secondary.base_address.address)

        # Coefficient '2' because amount pass two accounts. So two transactions = double tx_fee.
        self.assertEqual(wei2eth(secondary_balance), truncate(amount - 2 * constants.TX_FEE, constants.DECIMAL_PLACES))
