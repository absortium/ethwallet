__author__ = 'andrew.shvv@gmail.com'

from django.conf import settings

from core.utils.logging import getPrettyLogger
from ethwallet.models import Block
from ethwallet.rpc.client import get_rpc_client

logger = getPrettyLogger(__name__)


class BlockChainIterator():
    def __init__(self):
        self.blocks = {}
        self.client = get_rpc_client(host=settings.ETHNODE_URL)

        try:
            self.number = Block.objects.latest('number').number
        except Block.DoesNotExist:
            self.number = self.client.eth_blockNumber()

    def __iter__(self):
        return self

    def __next__(self):
        if self.number not in self.blocks.keys():
            block = self.client.eth_getBlockByNumber(self.number)

            if block is None:
                raise StopIteration()

            self.blocks[self.number] = block

        else:
            block = self.blocks[self.number]
        return block

    def forward(self):
        logger.debug("Forward {}".format(self.number))
        self.number += 1

    def back(self):
        logger.debug("Back {}".format(self.number))
        self.number -= 1
