import warnings

from .constants import BLOCK_TAGS, BLOCK_TAG_LATEST
from .exceptions import (BadRequest, BadResponse)
from .interfaces import HTTPInterface
from .utils import hex_to_dec, validate_block

_client = None


def get_rpc_client(*args, **kwargs):
    global _client
    if not _client:
        _client = RPCClient(*args, **kwargs)
    return _client


class RPCClient():
    def __init__(self, interface=HTTPInterface()):
        self.interface = interface

    def construct(self, method, params=None, _id=0):
        params = params or []
        data = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': _id,
        }

        return data

    def exec(self, method, params=None):
        data = self.construct(method=method, params=params)
        response = self.interface.send(data)

        if 'error' in response:
            raise BadRequest(response['error'])

        if 'jsonrpc' not in response:
            raise BadResponse("Without 'jsonrpc' version")
        else:
            if response['jsonrpc'] != "2.0":
                raise BadResponse("Bad json rpc version")

        try:
            print("Req:{} Resp:{}".format(data, response))
            return response['result']
        except KeyError:
            raise BadResponse("There is no 'result' section in: {} (Only 30 characters shown)".format(response[:30]))

    ################################################################################
    # Miner methods
    ################################################################################
    def miner_start(self, cpus=1):
        return self.exec('miner_start', params=[cpus])

    def miner_stop(self):
        return self.exec('miner_stop')

    ################################################################################
    # Personal methods
    ################################################################################
    def personal_unlockAccount(self, address, passphrase, duration=5):
        return self.exec('personal_unlockAccount', params=[address, passphrase, duration])

    def personal_newAccount(self, password):
        return self.exec('personal_newAccount', params=[password])

    ################################################################################
    # Web3 methods
    ################################################################################

    def web3_clientVersion(self):
        return self.exec('web3_clientVersion')

    def web3_sha3(self, data):
        data = str(data).encode('hex')
        return self.exec('web3_sha3', [data])

    ################################################################################
    # Net methods
    ################################################################################

    def net_version(self):
        return self.exec('net_version')

    def net_listening(self):
        return self.exec('net_listening')

    def net_peerCount(self):
        return hex_to_dec(self.exec('net_peerCount'))

    ################################################################################
    # Eth methods
    ################################################################################

    def eth_protocolVersion(self):
        return self.exec('eth_protocolVersion')

    def eth_syncing(self):
        return self.exec('eth_syncing')

    def eth_coinbase(self):
        return self.exec('eth_coinbase')

    def eth_mining(self):
        return self.exec('eth_mining')

    def eth_hashrate(self):
        return hex_to_dec(self.exec('eth_hashrate'))

    def eth_gasPrice(self):
        return hex_to_dec(self.exec('eth_gasPrice'))

    def eth_accounts(self):
        return self.exec('eth_accounts')

    def eth_blockNumber(self):
        return hex_to_dec(self.exec('eth_blockNumber'))

    def eth_getBalance(self, address=None, block=BLOCK_TAG_LATEST):
        address = address or self.eth_coinbase()
        block = validate_block(block)
        return hex_to_dec(self.exec('eth_getBalance', [address, block]))

    def eth_getStorageAt(self, address=None, position=0, block=BLOCK_TAG_LATEST):
        block = validate_block(block)
        return self.exec('eth_getStorageAt', [address, hex(position), block])

    def eth_getTransactionCount(self, address, block=BLOCK_TAG_LATEST):
        block = validate_block(block)
        return hex_to_dec(self.exec('eth_getTransactionCount', [address, block]))

    def eth_getBlockTransactionCountByHash(self, block_hash):
        return hex_to_dec(self.exec('eth_getBlockTransactionCountByHash', [block_hash]))

    def eth_getBlockTransactionCountByNumber(self, block=BLOCK_TAG_LATEST):
        block = validate_block(block)
        return hex_to_dec(self.exec('eth_getBlockTransactionCountByNumber', [block]))

    def eth_getUncleCountByBlockHash(self, block_hash):
        return hex_to_dec(self.exec('eth_getUncleCountByBlockHash', [block_hash]))

    def eth_getUncleCountByBlockNumber(self, block=BLOCK_TAG_LATEST):
        block = validate_block(block)
        return hex_to_dec(self.exec('eth_getUncleCountByBlockNumber', [block]))

    def eth_getCode(self, address, default_block=BLOCK_TAG_LATEST):
        if isinstance(default_block, str):
            if default_block not in BLOCK_TAGS:
                raise ValueError
        return self.exec('eth_getCode', [address, default_block])

    def eth_sign(self, address, data):
        return self.exec('eth_sign', [address, data])

    def eth_sendTransaction(self, to_address=None, from_address=None, gas=None, gas_price=None, value=None, data=None,
                            nonce=None):
        obj = {}
        obj['from'] = from_address or self.eth_coinbase()
        if to_address is not None:
            obj['to'] = to_address
        if gas is not None:
            obj['gas'] = hex(gas)
        if gas_price is not None:
            obj['gasPrice'] = hex(gas_price)
        if value is not None:
            obj['value'] = hex(value)
        if data is not None:
            obj['data'] = data
        if nonce is not None:
            obj['nonce'] = hex(nonce)
        return self.exec('eth_sendTransaction', params=[obj])

    def eth_sendRawTransaction(self, data):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_sendrawtransaction

        NEEDS TESTING
        """
        return self.exec('eth_sendRawTransaction', [{'data': data}])

    def eth_call(self, to_address, from_address=None, gas=None, gas_price=None, value=None, data=None,
                 default_block=BLOCK_TAG_LATEST):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_call

        NEEDS TESTING
        """
        if isinstance(default_block, str):
            if default_block not in BLOCK_TAGS:
                raise ValueError
        obj = {}
        obj['to'] = to_address
        if from_address is not None:
            obj['from'] = from_address
        if gas is not None:
            obj['gas'] = hex(gas)
        if gas_price is not None:
            obj['gasPrice'] = hex(gas_price)
        if value is not None:
            obj['value'] = value
        if data is not None:
            obj['data'] = data
        return self.exec('eth_call', [obj, default_block])

    def eth_estimateGas(self, to_address=None, from_address=None, gas=None, gas_price=None, value=None, data=None,
                        default_block=BLOCK_TAG_LATEST):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_estimategas

        NEEDS TESTING
        """
        if isinstance(default_block, str):
            if default_block not in BLOCK_TAGS:
                raise ValueError
        obj = {}
        if to_address is not None:
            obj['to'] = to_address
        if from_address is not None:
            obj['from'] = from_address
        if gas is not None:
            obj['gas'] = hex(gas)
        if gas_price is not None:
            obj['gasPrice'] = hex(gas_price)
        if value is not None:
            obj['value'] = value
        if data is not None:
            obj['data'] = data
        return self.exec('eth_estimateGas', [obj, default_block])

    def eth_getBlockByHash(self, block_hash, tx_objects=True):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblockbyhash

        TESTED
        """
        return self.exec('eth_getBlockByHash', [block_hash, tx_objects])

    def eth_getBlockByNumber(self, block=BLOCK_TAG_LATEST, tx_objects=True):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblockbynumber

        TESTED
        """
        block = validate_block(block)
        return self.exec('eth_getBlockByNumber', [block, tx_objects])

    def eth_getTransactionByHash(self, tx_hash):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyhash

        TESTED
        """
        return self.exec('eth_getTransactionByHash', [tx_hash])

    def eth_getTransactionByBlockHashAndIndex(self, block_hash, index=0):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyblockhashandindex

        TESTED
        """
        return self.exec('eth_getTransactionByBlockHashAndIndex', [block_hash, hex(index)])

    def eth_getTransactionByBlockNumberAndIndex(self, block=BLOCK_TAG_LATEST, index=0):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyblocknumberandindex

        TESTED
        """
        block = validate_block(block)
        return self.exec('eth_getTransactionByBlockNumberAndIndex', [block, hex(index)])

    def eth_getTransactionReceipt(self, tx_hash):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionreceipt

        TESTED
        """
        return self.exec('eth_getTransactionReceipt', [tx_hash])

    def eth_getUncleByBlockHashAndIndex(self, block_hash, index=0):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclebyblockhashandindex

        TESTED
        """
        return self.exec('eth_getUncleByBlockHashAndIndex', [block_hash, hex(index)])

    def eth_getUncleByBlockNumberAndIndex(self, block=BLOCK_TAG_LATEST, index=0):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclebyblocknumberandindex

        TESTED
        """
        block = validate_block(block)
        return self.exec('eth_getUncleByBlockNumberAndIndex', [block, hex(index)])

    def eth_getCompilers(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getcompilers

        TESTED
        """
        return self.exec('eth_getCompilers')

    def eth_compileSolidity(self, code):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_compilesolidity

        TESTED
        """
        return self.exec('eth_compileSolidity', [code])

    def eth_compileLLL(self, code):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_compilelll

        N/A
        """
        return self.exec('eth_compileLLL', [code])

    def eth_compileSerpent(self, code):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_compileserpent

        N/A
        """
        return self.exec('eth_compileSerpent', [code])

    def eth_newFilter(self, from_block=BLOCK_TAG_LATEST, to_block=BLOCK_TAG_LATEST, address=None, topics=None):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newfilter

        NEEDS TESTING
        """
        _filter = {
            'fromBlock': from_block,
            'toBlock': to_block,
            'address': address or [],
            'topics': topics or [],
        }
        return self.exec('eth_newFilter', [_filter])

    def eth_newBlockFilter(self, default_block=BLOCK_TAG_LATEST):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newblockfilter

        NEEDS TESTING
        """
        return self.exec('eth_newBlockFilter', [default_block])

    def eth_newPendingTransactionFilter(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newpendingtransactionfilter

        TESTED
        """
        return self.exec('eth_newPendingTransactionFilter')

    def eth_uninstallFilter(self, filter_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_uninstallfilter

        NEEDS TESTING
        """
        return self.exec('eth_uninstallFilter', [filter_id])

    def eth_getFilterChanges(self, filter_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterchanges

        NEEDS TESTING
        """
        return self.exec('eth_getFilterChanges', [filter_id])

    def eth_getFilterLogs(self, filter_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterlogs

        NEEDS TESTING
        """
        return self.exec('eth_getFilterLogs', [filter_id])

    def eth_getLogs(self, filter_object):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getlogs

        NEEDS TESTING
        """
        return self.exec('eth_getLogs', [filter_object])

    def eth_getWork(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getwork

        TESTED
        """
        return self.exec('eth_getWork')

    def eth_submitWork(self, nonce, header, mix_digest):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_submitwork

        NEEDS TESTING
        """
        return self.exec('eth_submitWork', [nonce, header, mix_digest])

    def eth_submitHashrate(self, hash_rate, client_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_submithashrate

        TESTED
        """
        return self.exec('eth_submitHashrate', [hex(hash_rate), client_id])

    ################################################################################
    # Db methods
    ################################################################################

    def db_putString(self, db_name, key, value):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_putstring

        TESTED
        """
        warnings.warn('deprecated', DeprecationWarning)
        return self.exec('db_putString', [db_name, key, value])

    def db_getString(self, db_name, key):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_getstring

        TESTED
        """
        warnings.warn('deprecated', DeprecationWarning)
        return self.exec('db_getString', [db_name, key])

    def db_putHex(self, db_name, key, value):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_puthex

        TESTED
        """
        if not value.startswith('0x'):
            value = '0x{}'.format(value)
        warnings.warn('deprecated', DeprecationWarning)
        return self.exec('db_putHex', [db_name, key, value])

    def db_getHex(self, db_name, key):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_gethex

        TESTED
        """
        warnings.warn('deprecated', DeprecationWarning)
        return self.exec('db_getHex', [db_name, key])

    ################################################################################
    # Shh methods
    ################################################################################

    def shh_version(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_version

        N/A
        """
        return self.exec('shh_version')

    def shh_post(self, topics, payload, priority, ttl, from_=None, to=None):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_post

        NEEDS TESTING
        """
        whisper_object = {
            'from': from_,
            'to': to,
            'topics': topics,
            'payload': payload,
            'priority': hex(priority),
            'ttl': hex(ttl),
        }
        return self.exec('shh_post', [whisper_object])

    def shh_newIdentity(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newidentity

        N/A
        """
        return self.exec('shh_newIdentity')

    def shh_hasIdentity(self, address):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_hasidentity

        NEEDS TESTING
        """
        return self.exec('shh_hasIdentity', [address])

    def shh_newGroup(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newgroup

        N/A
        """
        return self.exec('shh_newGroup')

    def shh_addToGroup(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_addtogroup

        NEEDS TESTING
        """
        return self.exec('shh_addToGroup')

    def shh_newFilter(self, to, topics):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newfilter

        NEEDS TESTING
        """
        _filter = {
            'to': to,
            'topics': topics,
        }
        return self.exec('shh_newFilter', [_filter])

    def shh_uninstallFilter(self, filter_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_uninstallfilter

        NEEDS TESTING
        """
        return self.exec('shh_uninstallFilter', [filter_id])

    def shh_getFilterChanges(self, filter_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_getfilterchanges

        NEEDS TESTING
        """
        return self.exec('shh_getFilterChanges', [filter_id])

    def shh_getMessages(self, filter_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_getmessages

        NEEDS TESTING
        """
        return self.exec('shh_getMessages', [filter_id])
