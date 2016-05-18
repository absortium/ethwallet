__author__ = 'andrew.shvv@gmail.com'

from core.utils.logging import getLogger
from ethwallet.celery.tasks import check_block
from ethwallet.constants import CONFIRMATIONS_FOR_NOTIFICATION
from ethwallet.model.models import Block, Transaction
from ethwallet.tests.base import EthWalletUnitTest

logger = getLogger(__name__)


class EthnodeTest(EthWalletUnitTest):
    def setUp(self):
        super().setUp()

        # Create address
        self.address = self.create_address()
        self.mock_notification()

    def tearDown(self):
        self.unmock_notification()
        super().tearDown()

    def _init_node_data(self, start=0, end=1, need_transaction=True):
        blocks = []
        for i in range(start, end):
            block = {
                "hash": hex(i),
                "number": hex(i),
                "parentHash": hex(i-1) if i > 0 else hex(0),
                "timestamp": "0x5735223a"
            }

            if need_transaction:
                block.update(transactions=[
                    {
                        "blockNumber": hex(i),
                        "from": hex(i),
                        "hash": hex(i),
                        "to": self.address["address"],
                        "value": "0x1"
                    }
                ])

            blocks.append(block)

        # Set rpc data which will be returned by RPC client.
        self.set_rpcclient_data(blocks=blocks)

    def _init_db_data(self, start=0, end=1, diff_hashes=False, need_transaction=True):
        for i in range(start, end):
            if diff_hashes:
                b = Block(number=i, hash="some another hash {}".format(hex(i)))
            else:
                b = Block(number=i, hash=hex(i))

            for t in Transaction.objects.all():
                confirmations = b.number - t.block_number + 1
                if confirmations >= CONFIRMATIONS_FOR_NOTIFICATION:
                    t.notified = True
                    t.save()

            b.save()

            if need_transaction:
                t = Transaction(from_address=hex(i),
                                to_address=self.address["address"],
                                value=0x01,
                                hash=hex(i),
                                owner_id=self.address['pk'],
                                block_number=i)
                t.save()

    def test_the_same_hash(self):
        """
            Test case with the same last hashes and last updated block. We should hang up couple of new blocks.
        """
        self._init_node_data(end=3)
        self._init_db_data(end=1)

        # Simulate celery task execution
        check_block.delay()

    def test_the_different_hash(self):
        """
            Test case with the same last hashes but not full history of blocks. We should roll back for a couple of blocks
            and then hang up.
        """

        self._init_node_data(end=5)
        self._init_db_data(end=2)
        self._init_db_data(start=2, end=5, diff_hashes=True)

        # Simulate celery task execution
        check_block.delay()

        transactions = Transaction.objects.all()
        self.assertEqual(len(transactions), 5)

    def test_transaction_already_exist(self):
        pass

    def test_the_transaction_notification(self):
        """
            Test case where transaction confirmation exceed number of confirmation is needed for its deletion.
        """

        transaction_value = 1
        count_of_transaction = 10
        count_of_blocks = count_of_transaction
        count_of_notifications = count_of_blocks - CONFIRMATIONS_FOR_NOTIFICATION + 1
        sum_value = count_of_notifications * transaction_value

        self._init_node_data(end=count_of_blocks)
        self._init_db_data(end=1)

        # Simulate celery task execution
        check_block.delay()

        notifications = self.get_notification()

        for webhook, addresses in notifications.items():
            for address, transactions in addresses.items():
                hashes = [tx_hash for tx_hash, _ in transactions]

                # should be notification with the same tx hash
                self.assertEqual(len(hashes), len(set(hashes)))
                self.assertEqual(len(hashes), count_of_notifications)

                values = [value for _, value in transactions]
                self.assertEqual(sum_value, sum(values))
