from copy import deepcopy
from random import choice
from string import ascii_letters

from mock import patch

from core.utils.logging import getLogger
from ethwallet.utils import eth2wei, generate_token, register

__author__ = 'andrew.shvv@gmail.com'

logger = getLogger(__name__)

states = [{
    "blocks": [{
        'hash': '1a659fd7de8636f2f1ac22bc35248aa68cd1e5f6',
        'number': '0x0',
        'transactions': []
    }]
}]

operations = []


class RPCClientMockMixin():
    """
        EthnodeMockMixin substitute original rpc client and return mock block information.
    """

    def __init__(self):
        # WARNING!: Be careful with names you may override variables in the class that inherit this mixin!
        self._rpcclient_patcher = None

    def flush_rpc_state(self):
        global states
        states = [states[0]]

    def mock_rpcclient(self):
        self.flush_rpc_state()

        self._rpcclient_patcher = patch('ethwallet.rpc.client.RPCClient', new=MockEthRPCClient)
        self._rpcclient_patcher.start()

    def unmock_rpcclient(self):
        self._rpcclient_patcher.stop()

    def get_block_chain(self):
        global states
        return states[-1]["blocks"]

    def change_block_chain(self, *args, **kwargs):
        global states

        if kwargs.get('fork', False):
            self.revert_block_chain()

        state = deepcopy(states[-1])
        for change in args:
            state = change(state)

        states.append(state)

    def revert_block_chain(self):
        global states
        del states[-1]

    def add_block(self, *transactions):
        def change(state):
            block_number = int(state["blocks"][-1]["number"], 16) + 1

            block = {
                "hash": generate_token(),
                "number": hex(block_number),
                "transactions": []
            }

            for transaction in transactions:
                from_address = transaction[0]
                to_address = transaction[1]
                value = transaction[2]

                try:
                    tx_hash = transaction[3]
                except IndexError:
                    tx_hash = None

                block["transactions"].append({
                    "blockNumber": hex(block_number),
                    "from": from_address,
                    "to": to_address,
                    "hash": tx_hash or generate_token(),
                    "value": str(eth2wei(value))
                })

            state["blocks"].append(block)

            return state

        return change


class MockEthRPCClient():
    def __init__(self, *args, **kwargs):
        super().__init__()

    @register(operations)
    def eth_getBalance(self, *args, **kwargs):
        return 1000

    @register(operations)
    def personal_unlockAccount(self, *args, **kwargs):
        pass

    @register(operations)
    def eth_sendTransaction(self, *args, **kwargs):
        return "some_transaction_hash"

    @register(operations)
    def eth_getBlockByNumber(self, block_number):
        global states
        for block in states[-1]["blocks"]:
            if int(block["number"], 16) == block_number:
                return block
        return None

    @register(operations)
    def eth_blockNumber(self, *args, **kwargs):
        global states
        return int(states[-1]["blocks"][-1]["number"], 16)

    @register(operations)
    def personal_newAccount(self, *args, **kwargs):
        s = ascii_letters + "0123456789"
        address = "".join([choice(s) for _ in range(30)])
        return address
