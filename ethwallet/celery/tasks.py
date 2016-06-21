__author__ = 'andrew.shvv@gmail.com'

import requests
from celery import shared_task
from django.conf import settings
from django.db import transaction
from pprintpp import pprint as print

from core.utils.logging import getPrettyLogger
from ethwallet import constants
from ethwallet import notifications
from ethwallet.celery.base import get_base_class
from ethwallet.constants import CONFIRMATIONS_FOR_NOTIFICATION
from ethwallet.models import Transaction, Address, Block
from ethwallet.notifications import get_notify_client
from ethwallet.rpc.client import get_rpc_client

logger = getPrettyLogger(__name__)


def add_new_transactions(transactions):
    for bt in transactions:
        try:
            # Check - do we have such transaction address in our db?
            address = Address.objects.get(address=bt['to'])
        except Address.DoesNotExist:
            logger.debug(["Continue:", bt['to']])
            continue

        logger.debug(["Check:", bt['to']])

        t_hash = bt['hash']
        t_from_address = bt['from']
        t_to_address = bt['to']
        t_block_number = int(bt['blockNumber'], 16)
        t_value = int(bt['value'], 16)

        try:
            # This case means that we already proceed the transaction, which
            # may happens while blockchain fork, so we should change the block number
            st = address.transactions.get(hash=bt['hash'])
            st.block_number = int(bt['blockNumber'], 16)

        except Transaction.DoesNotExist:
            st = Transaction(hash=t_hash,
                            from_address=t_from_address,
                            to_address=t_to_address,
                            block_number=t_block_number,
                            owner_id=address.pk,
                            value=t_value)
            st.save()


def send_notifications(transactions, block_number):
    nc = get_notify_client()

    for t in transactions:
        confirmations = block_number - t.block_number + 1
        if not t.notified and confirmations >= CONFIRMATIONS_FOR_NOTIFICATION:
            t.notified = True
            address = Address.objects.get(address=t.to_address)

            nc.notify(webhook=address.owner.webhook,
                      address=address.address,
                      tx_hash=t.hash,
                      value=t.value)

        t.save()


@shared_task(bind=True, base=get_base_class())
def check_block(self):
    with notifications.atomic():
        with transaction.atomic():
            def add_new_block(nodeblock, n):
                block_number = int(nodeblock['number'], 16)

                add_new_transactions(nodeblock['transactions'])
                send_notifications(Transaction.objects.all(), block_number)

                dbblock = Block(number=block_number, hash=nodeblock['hash'])
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

            # logger.debug('Get RPC Client')
            client = get_rpc_client(host=settings.ETHNODE_URL)

            try:
                n = Block.objects.latest('number').number
            except Block.DoesNotExist:
                n = client.eth_blockNumber()
            # logger.debug('Get last unprocessed block: {}'.format(n))

            nodeblock = client.eth_getBlockByNumber(n)
            while nodeblock is not None:
                try:
                    # logger.debug('Block #{} - check block'.format(n))
                    n = check_block(nodeblock, n)
                except Block.DoesNotExist:
                    n = add_new_block(nodeblock, n)

                nodeblock = client.eth_getBlockByNumber(n)


@shared_task(bind=True, max_retries=constants.CELERY_MAX_RETRIES, base=get_base_class())
def notify_user(self, webhook, address, tx_hash, value):
    data = {
        'address': address,
        'amount': value,
        'tx_hash': tx_hash
    }

    try:
        logger.debug("Notify", data, webhook)
        requests.post(webhook, address, data=data)
    except Exception as e:
        print(e)
        raise self.retry(countdown=constants.NOTIFY_RETRY_COUNTDOWN)
