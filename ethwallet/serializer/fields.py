from rest_framework.exceptions import ValidationError

from ethwallet import constants
from ethwallet.utils import wei2eth

__author__ = 'andrew.shvv@gmail.com'

from rest_framework import serializers


class TransactionBlockNumber(serializers.IntegerField):
    def to_internal_value(self, value):
        if not isinstance(value, str):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(value).__name__)

        try:
            return int(value, 16)
        except (ValueError, TypeError):
            raise ValidationError("Should be hex string.")


class TransactionValue(serializers.IntegerField):
    def to_internal_value(self, value):
        if not isinstance(value, str):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(value).__name__)

        try:
            return wei2eth(int(value, 16))
        except (ValueError, TypeError):
            raise ValidationError("Should be hex string.")
