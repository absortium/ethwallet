from django.contrib.auth import settings
from django.core.management.base import BaseCommand

from core.utils.logging import getPrettyLogger
from ethwallet.rpc import get_rpc_client
from pprint import pprint
logger = getPrettyLogger(__name__)

__author__ = 'andrew.shvv@gmail.com'


class Command(BaseCommand):
    help = 'Create json file from ethnode rpc response of getBlockByNumber function in range of blocks [from, to]'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--from',  type=int)
        parser.add_argument('--to', type=int)

    def handle(self, *args, **options):
        client = get_rpc_client(host=settings.ETHNODE_URL)

        from_block = options['from']
        to_block = options['to']

        if to_block is None:
            to_block = client.eth_blockNumber()

        if from_block is None:
            from_block = to_block - 20

        blocks = [client.eth_getBlockByNumber(n) for n in range(from_block, to_block)]

        pprint(blocks)
