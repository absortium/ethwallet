import requests
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from requests.exceptions import ConnectionError, ConnectTimeout
from rest_framework.exceptions import ValidationError

from core.utils.logging import getPrettyLogger
from ethwallet import constants
from ethwallet import notifications
from ethwallet import sendethereum
from ethwallet.celery.base import get_base_class
from ethwallet.models import Transaction, Address, Block
from ethwallet.notifications import get_notify_client
from ethwallet.rpc.client import get_rpc_client
from ethwallet.rpc.iterator import BlockChainIterator
from ethwallet.sendethereum import get_send_client
from ethwallet.serializer.serializers import TransactionSerializer
from ethwallet.utils import get_wallet_password, eth2wei

__author__ = 'andrew.shvv@gmail.com'

logger = getPrettyLogger(__name__)


def add_new_block(block):
    add_new_transactions(block['transactions'])

    block_number = int(block['number'], 16)
    Block(number=block_number, hash=block['hash']).save()


def add_new_transactions(transactions):
    def deserialize(t):
        serializer = TransactionSerializer(data=t)
        serializer.is_valid(raise_exception=True)
        return serializer.object()

    def send_to_base(t):
        # If we receive new transaction from some external ethereum address than we should redirect ethereum
        # on base user account.

        sc = get_send_client()

        base_user_address = Address.objects.get(owner=t.owner, is_base_address=True)

        sc.send(from_address=t.to_address,
                to_address=base_user_address.address,
                value=t.value,
                user_pk=t.owner.pk)

    def send_notifications(t):
        # If transaction is received on the base address this means that it is our transaction that we
        # redirected previously, so we should notify user that he can use money now.

        nc = get_notify_client()
        if t.notification_status == constants.NOTIFICATION_INIT:
            t.notification_status = constants.NOTIFICATION_PENDING

            nc.notify(tx_pk=t.pk)

    for t in transactions:
        try:
            t = deserialize(t)
        except ValidationError as e:
            continue

        try:
            address = Address.objects.get(address=t.to_address)
        except Address.DoesNotExist:
            continue

        t.owner = address.owner

        if address.is_base_address:
            send_notifications(t)
        elif not t.is_spent:
            send_to_base(t)

        t.save()


@shared_task(bind=True, base=get_base_class())
def check_block(self):
    block_chain = BlockChainIterator()

    for block in block_chain:
        with notifications.atomic():
            with sendethereum.atomic():
                with transaction.atomic():
                    try:
                        dbblock = Block.objects.get(number=int(block['number'], 16))

                        if block['hash'] == dbblock.hash:
                            block_chain.forward()
                        else:
                            # In case of block chain fork we should delete block with wrong hash
                            # and rollback to the previous one.

                            dbblock.delete()
                            block_chain.back()

                    except Block.DoesNotExist:
                        add_new_block(block)
                        block_chain.forward()


@shared_task(bind=True, max_retries=constants.SEND_MAX_RETRIES, base=get_base_class())
def send(self, user_pk, from_address, to_address, value):
    try:

        User = get_user_model()
        user = User.objects.get(pk=user_pk)

        password = get_wallet_password(user.wallet_secret_key)

        client = get_rpc_client(host=settings.ETHNODE_URL)
        client.personal_unlockAccount(address=from_address, passphrase=password)

        balance = client.eth_getBalance()
        value = eth2wei(value)

        if balance >= value:
            client.eth_sendTransaction(from_address=from_address,
                                       to_address=to_address,
                                       value=value)
        else:
            raise ValidationError("Not enough money")

    except (ConnectionError, ConnectTimeout) as e:
        raise self.retry(countdown=constants.SEND_RETRY_COUNTDOWN)


@shared_task(bind=True, max_retries=constants.NOTIFY_MAX_RETRIES, base=get_base_class())
def notify_user(self, tx_pk):
    t = Transaction.objects.get(pk=tx_pk)

    data = {
        'address': t.to_address,
        'amount': t.value,
        'tx_hash': t.hash
    }

    try:
        requests.post(t.owner.web_hook, data=data)
        t.notification_status = constants.NOTIFICATION_DONE
        t.save()

    except (ConnectionError, ConnectTimeout) as e:
        raise self.retry(countdown=constants.NOTIFY_RETRY_COUNTDOWN)
