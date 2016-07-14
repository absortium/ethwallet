from decimal import Decimal

from ethwallet import constants

__author__ = 'andrew.shvv@gmail.com'
import mock

from core.utils.logging import getLogger
from ethwallet.celery.tasks import check_block, notify_user
from ethwallet.models import Block, Transaction
from ethwallet.tests.base import EthWalletUnitTest

logger = getLogger(__name__)


class EthnodeTest(EthWalletUnitTest):
    def setUp(self):
        super().setUp()

        # Create user address
        self.address = self.create_address()["address"]

        self.notification_flush()
        self.flush_rpc_state()

        # Create first block
        check_block.delay()

    def tearDown(self):
        super().tearDown()

    def test_block_chain_mixin(self):
        self.change_block_chain(
            self.add_block(
                ("1", self.address, "2"),
                ("1", self.address, "2"),
                ("1", self.address, "2")
            )
        )

        self.assertEqual(len(self.get_block_chain()), 2)

    def test_block_chain_iterator(self):
        self.change_block_chain(
            self.add_block(
                ("1", self.address, "2"),
                ("1", self.address, "2"),
                ("1", self.address, "2")
            )
        )

        check_block.delay()
        self.assertEqual(len(Block.objects.all()), 2)

    def test_count_of_transactions(self):
        self.change_block_chain(
            self.add_block(
                ("1", self.address, "2"),
                ("1", self.address, "2"),
                ("1", self.address, "2")
            )
        )
        check_block.delay()

        transactions = Transaction.objects.filter(owner=self.user)
        self.assertEqual(len(transactions), 3)

    def test_value_of_transactions(self):
        self.change_block_chain(
            self.add_block(
                ("1", self.address, "2"),
                ("1", self.address, "2"),
                ("1", self.address, "2")
            )
        )
        check_block.delay()

        for transaction in Transaction.objects.filter(owner=self.user):
            self.assertEqual(transaction.value, Decimal("2"))

    def test_count_of_transactions_another(self):
        self.change_block_chain(
            self.add_block(
                ("1", "some another address", "2"),
                ("1", "some another address", "2"),
                ("1", "some another address", "2")
            )
        )
        check_block.delay()

        transactions = Transaction.objects.filter(owner=self.user)
        self.assertEqual(len(transactions), 0)

    def test_notification_count(self):
        base_address = self.user.base_address.address

        self.change_block_chain(
            self.add_block(
                ("1", base_address, "2"),
                ("1", base_address, "2"),
                ("1", base_address, "2")
            )
        )
        check_block.delay()

        self.assertEqual(len(self.get_notifications()), 3)

    @mock.patch('requests.post', mock.Mock())
    def test_notify_user(self):
        # Create transaction
        t = Transaction.objects.create(from_address="1",
                                       to_address="2",
                                       value=100,
                                       block_number=1,
                                       notification_status=constants.NOTIFICATION_PENDING,
                                       owner_id=self.user.pk)

        # Process this transaction
        notify_user.delay(t.pk)

        self.assertEqual(Transaction.objects.get(pk=t.pk).notification_status, constants.NOTIFICATION_DONE)

    def test_block_fork(self):
        base_address = self.user.base_address.address

        self.change_block_chain(self.add_block())
        check_block.delay()

        self.change_block_chain(self.add_block(), fork=True)
        check_block.delay()

        self.assertEqual(len(Block.objects.all()), 2)

    def test_same_transaction_in_two_blocks_1(self):
        base_address = self.user.base_address.address

        self.change_block_chain(self.add_block(("1", base_address, "2", "some_hash")))
        check_block.delay()

        self.change_block_chain(self.add_block(("1", base_address, "2", "some_hash")), fork=True)
        check_block.delay()

        self.assertEqual(len(self.get_notifications()), 1)
        self.assertEqual(len(Transaction.objects.all()), 1)

    def test_not_base_address(self):
        self.change_block_chain(self.add_block(("1", self.address, "2")))
        check_block.delay()

        self.assertEqual(len(self.get_notifications()), 0)

    def test_same_transaction_in_two_blocks_2(self):
        self.change_block_chain(self.add_block(("1", self.address, "2", "some_hash")))
        check_block.delay()

        self.change_block_chain(self.add_block(("1", self.address, "2", "some_hash")), fork=True)
        check_block.delay()

        self.assertEqual(len(self.get_notifications()), 0)
