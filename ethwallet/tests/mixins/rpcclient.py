from random import choice
from string import ascii_letters

from mock import patch

from core.utils.logging import getLogger

__author__ = 'andrew.shvv@gmail.com'

logger = getLogger(__name__)

_blocks = None

operations = []


def register(debug=False):
    def wrapper(func):
        def decorator(*args, **kwargs):
            global operations

            operation = {
                'func': func.__name__,
                'args': args,
                'kwargs': kwargs
            }

            if debug:
                logger.debug(operation)

            operations.append(operation)

            return func(*args, **kwargs)

        return decorator

    return wrapper


class RPCClientMockMixin():
    """
        EthnodeMockMixin substitute original rpc client and return mock block information.
    """

    def __init__(self):
        # WARNING!: Be careful with names you may override variables in the class that inherit this mixin!
        self._rpcclient_patcher = None

    def set_rpcclient_data(self, blocks=[]):
        global _blocks
        if _blocks is not None:
            _blocks += blocks
        else:
            _blocks = blocks

    def mock_rpcclient(self):
        global _blocks
        _blocks = None

        self._rpcclient_patcher = patch('ethwallet.rpc.client.RPCClient', new=MockEthRPCClient)
        self._rpcclient_patcher.start()

    def unmock_rpcclient(self):
        self._rpcclient_patcher.stop()


class MockEthRPCClient():
    def __init__(self, *args, **kwargs):
        super().__init__()

    @register()
    def eth_getBalance(self, *args, **kwargs):
        return 1000

    @register()
    def personal_unlockAccount(self, *args, **kwargs):
        pass

    @register()
    def eth_sendTransaction(self, *args, **kwargs):
        return "some_transaction_hash"

    @register()
    def eth_getBlockByNumber(self, block_number):
        global _blocks
        for block in _blocks:
            if int(block["number"], 16) == block_number:
                return block
        return None

    @register()
    def eth_blockNumber(self, *args, **kwargs):
        global _blocks
        prev_number = -1
        for block in _blocks:
            number = int(block["number"], 16)
            if not number > prev_number:
                raise Exception("Previous block number less that forward block number")
            prev_number = number

        return prev_number

    @register()
    def personal_newAccount(self, *args, **kwargs):
        s = ascii_letters + "0123456789"
        address = "".join([choice(s) for _ in range(30)])
        return address
