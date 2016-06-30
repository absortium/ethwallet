from ethwallet.utils import wei2eth

__author__ = 'andrew.shvv@gmail.com'

from core.utils.logging import getLogger
from ethwallet.serializer.serializers import TransactionSerializer
from ethwallet.tests.base import EthWalletUnitTest

logger = getLogger(__name__)


class TransactionTest(EthWalletUnitTest):
    def test_deserialization(self):
        transaction = {
            "blockHash": "0xb99edeb79f76814d950c54dda47699d1c4ed248264d289ab8ff5245e3aa49375",
            "blockNumber": "0x11ec51",
            "from": "0x7c0d52faab596c08f484e3478aebc6205f3f5d8c",
            "gas": "0x2fd618",
            "gasPrice": "0x4a817c800",
            "hash": "0x5585e04e99c5572c4f3dbd2ccd1949fe8e419b5355922d9ee61c4a1e735dbe1e",
            "nonce": "0x10c5c2",
            "to": "0x660cdfdf3d0e7443e7935343a1131b961575ccc7",
            "transactionIndex": "0x0",
            "value": "0x78cad1e25d0000"
        }

        serializer = TransactionSerializer(data=transaction)
        serializer.is_valid(raise_exception=True)
        t = serializer.object()

        self.assertEqual(t.block_number, int(transaction['blockNumber'], 16))
        self.assertEqual(t.value, wei2eth(int(transaction['value'], 16)))
        self.assertEqual(t.hash, transaction['hash'])
        self.assertEqual(t.from_address, transaction['from'])
        self.assertEqual(t.to_address, transaction['to'])
