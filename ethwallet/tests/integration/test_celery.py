__author__ = 'andrew.shvv@gmail.com'

from django.conf import settings
from core.utils.logging import getLogger
from ethwallet.rpc.client import RPCClient
from ethwallet.rpc.interfaces import HTTPInterface
from ethwallet.tests.base import EthWalletLiveTest

logger = getLogger(__name__)


class AccuracyTest(EthWalletLiveTest):
    def test_send_transactions(self, *args, **kwargs):
        """
            In order to execute this test celery worker should use django test db, for that you should set
            the CELERY_TEST=True environment variable in the worker(celery) service. See docker-compose.yml
        """

        # 1. Get main address (We can use data fixtures with already created user or just do it with rpc client).
        client = RPCClient(HTTPInterface(host=settings.ETHNODE_URL))
        addresses = client.eth_accounts()
        self.assertEqual(len(addresses), 1)
        coinbase = addresses[0]

        # 2. Check balance (Do it over RPC client).
        coinbase_balance = client.eth_getBalance(address=coinbase)

        # 3. Create bunch of another addresses (This should be done over self.create_address()).
        addresses = []
        count = 10
        for _ in range(count):
            address = self.create_address()
            addresses.append(address)

            # 4. Send transactions to (Do it over RPC client).
            client.eth_sendTransaction(from_address=coinbase,
                                       to_address=address['address'],
                                       value=coinbase_balance / count)

        self.wait_celery()

        # 5. Check address's balances
        for address in addresses:
            balance = client.eth_getBalance(address=address)
            self.assertEqual(balance, coinbase_balance / count)

        # 6. Check count of notification should be equal count of transactions.
        self.assertEqual(count)