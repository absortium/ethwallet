__author__ = 'andrew.shvv@gmail.com'

import requests
from celery import shared_task
from django.conf import settings
from django.db import transaction
from pprintpp import pprint as print

from core.utils.logging import getPrettyLogger
from ethwallet import constants
from ethwallet.celery.base import get_base_class
from ethwallet.constants import CONFIRMATIONS_FOR_NOTIFICATION
from ethwallet.model.models import Transaction, Address, Block
from ethwallet.rpc.client import get_rpc_client
from ethwallet.rpc.interfaces import HTTPInterface

logger = getPrettyLogger(__name__)


@shared_task(bind=True, base=get_base_class())
def check_block(self):
    with transaction.atomic():
        client = get_rpc_client(interface=HTTPInterface(host=settings.ETHNODE_URL))

        def add_new_block(nodeblock, n):
            for transaction in nodeblock['transactions']:
                try:
                    address = Address.objects.get(address=transaction['to'])
                except Address.DoesNotExist:
                    continue

                try:
                    t = address.transactions.get(hash=transaction['hash'])
                    t.block_number = int(transaction['blockNumber'], 16)

                except Transaction.DoesNotExist:
                    t = Transaction(hash=transaction['hash'],
                                    from_address=transaction['from'],
                                    to_address=transaction['to'],
                                    block_number=int(transaction['blockNumber'], 16),
                                    owner_id=address.pk,
                                    value=int(transaction['value'], 16))
                t.save()

            for transaction in Transaction.objects.all():
                confirmations = int(nodeblock['number'], 16) - transaction.block_number + 1

                if not transaction.notified and confirmations >= CONFIRMATIONS_FOR_NOTIFICATION:
                    transaction.notified = True
                    address = Address.objects.get(address=transaction.to_address)
                    notify_user.delay(webhook=address.owner.webhook,
                                      address=address.address,
                                      tx_hash=transaction.hash,
                                      value=transaction.value)

                transaction.save()

            dbblock = Block(number=int(nodeblock['number'], 16), hash=nodeblock['hash'])
            dbblock.save()
            n += 1
            return n

        def check_block(realblock, n):
            dbblock = Block.objects.get(number=n)

            if realblock['hash'] == dbblock.hash:
                n += 1

            else:
                dbblock.delete()
                n -= 1

            return n

        n = Block.objects.latest('number').number
        nodeblock = client.eth_getBlockByNumber(n)

        while nodeblock is not None:
            try:
                n = check_block(nodeblock, n)
            except Block.DoesNotExist:
                n = add_new_block(nodeblock, n)

            nodeblock = client.eth_getBlockByNumber(n)


@shared_task(bind=True, max_retries=constants.CELERY_MAX_RETRIES, base=get_base_class())
def notify_user(self, webhook, address, tx_hash, value):
    data = {
        'address': address,
        'value': value,
        'tx_hash': tx_hash
    }

    try:
        requests.post(webhook, data=data)
    except Exception as e:
        print(e)
        raise self.retry(countdown=constants.NOTIFY_RETRY_COUNTDOWN)
