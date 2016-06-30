from core.serializer.fields import MyChoiceField
from ethwallet import constants

__author__ = 'andrew.shvv@gmail.com'

from rest_framework import serializers

from core.utils.logging import getPrettyLogger
from ethwallet.models import Address, Transaction
from ethwallet.serializer.fields import TransactionBlockNumber, TransactionValue

logger = getPrettyLogger(__name__)


class AddressSerializer(serializers.ModelSerializer):
    amount = serializers.ReadOnlyField()
    address = serializers.ReadOnlyField()

    class Meta:
        model = Address
        fields = ('amount', 'address', 'created')
        lookup_field = 'address'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._object = None

    def object(self, **kwargs):
        if not self._object:
            validated_data = dict(
                list(self.validated_data.items()) +
                list(kwargs.items())
            )

            self._object = Address(**validated_data)
        return self._object


class TransactionSerializer(serializers.ModelSerializer):
    block_number = TransactionBlockNumber()
    value = TransactionValue()

    notification_status = MyChoiceField(choices=constants.AVAILABLE_NOTIFICATIONS_STATUS,
                                        default=constants.NOTIFICATION_INIT,
                                        read_only=True)

    class Meta:
        model = Transaction
        fields = ('from_address', 'to_address', 'value', 'block_number', 'hash', 'notification_status')

    def __init__(self, *args, **kwargs):
        kwargs['data'] = TransactionSerializer.normalize(kwargs['data'])

        super().__init__(*args, **kwargs)
        self._object = None

    @staticmethod
    def normalize(t):
        return {
            'from_address': t.get('from'),
            'to_address': t.get('to'),
            'value': t.get('value'),
            'block_number': t.get('blockNumber'),
            'hash': t.get('hash')
        }

    def object(self, **kwargs):
        if not self._object:
            validated_data = dict(
                list(self.validated_data.items()) +
                list(kwargs.items())
            )

            self._object = Transaction(**validated_data)
        return self._object
