import time

__author__ = 'andrew.shvv@gmail.com'

from django.conf import settings

from core.utils.logging import getLogger
from ethwallet.models import Address, Transaction
from ethwallet.rpc.client import RPCClient
from ethwallet.rpc.interfaces import HTTPInterface
from ethwallet.tests.base import EthWalletLiveTest
from ethwallet.celery import tasks

logger = getLogger(__name__)


class AccuracyTest(EthWalletLiveTest):
    def setUp(self):
        super().setUp()

        # Create Address with coinbase address in order to have ability to send transaction from it.
        self.rpcclient = RPCClient(HTTPInterface(host=settings.ETHNODE_URL))
        self.coinbase = self.rpcclient.eth_coinbase()

        # Be careful, do not change key argument because it is used for generating the address password,
        # otherwise you will have to recreate the address with preallocated amount of ethereum.
        address = Address(address=self.coinbase, owner_id=self.user.pk, key="somekey")
        address.save()

    def test_send_transactions(self, *args, **kwargs):
        """
            In order to execute this test celery worker should use django test db, for that you should set
            the CELERY_TEST=True environment variable in the worker(celery) service. See docker-compose.yml
        """
        tasks.check_block.delay()

        coinbase_balance = self.rpcclient.eth_getBalance(address=self.coinbase)

        addresses = []

        count_of_transaction = 5
        amount = int(coinbase_balance / count_of_transaction)
        for _ in range(count_of_transaction):
            address = self.create_address()['address']
            self.send_eth(amount=amount,
                          from_address=self.coinbase,
                          to_address=address,
                          debug=True)
            addresses.append(address)

        times = 5
        for _ in range(times):
            tasks.check_block.delay()
            time.sleep(10)

        for address in addresses:
            balance = self.rpcclient.eth_getBalance(address=address, block='pending')
            self.assertEqual(balance, amount)

        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), count_of_transaction)

        for transaction in transactions:
            self.assertEqual(transaction.value, amount)
            self.assertEqual(transaction.notified, True)
