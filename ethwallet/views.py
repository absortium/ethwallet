__author__ = 'andrew.shvv@gmail.com'
import binascii
import hashlib

from django.conf import settings
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response

from core.utils.logging import getPrettyLogger
from ethwallet.model.models import Address
from ethwallet.serializer.serializers import AddressSerializer
from ethwallet.utils import random_string

logger = getPrettyLogger(__name__)
from ethwallet.rpc import get_rpc_client


class AddressViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = AddressSerializer

    def get_queryset(self):
        return self.request.user.addresses.all()

    def get_address_password(self, key):
        if type(key) is not bytes:
            key = key.encode()

        salt = settings.SECRET_KEY.encode()
        dk = hashlib.pbkdf2_hmac('sha256', password=key, salt=salt, iterations=10000)

        return binascii.hexlify(dk).decode()

    @detail_route(methods=['post'])
    def send(self, request, pk, *args, **kwargs):
        from_address = pk
        to_address = request.data.get('address')
        try:
            amount = request.data.get('amount')
            if not amount:
                raise ValidationError("Specify 'amount' parameter")
            amount = int(amount)

        except ValueError:
            raise ValidationError("Parameter 'amount' should be int deserializable")

        if not to_address:
            raise ValidationError('Output address is not specified')

        try:
            address = request.user.addresses.get(address=from_address)
            password = self.get_address_password(address.key)

            client = get_rpc_client(host=settings.ETHNODE_URL)
            balance = client.eth_getBalance(address=to_address)

            if balance >= amount:
                client.personal_unlockAccount(address=from_address, passphrase=password)
                client.eth_sendTransaction(from_address=from_address, to_address=to_address, value=amount)
            else:
                raise ValidationError("Not enough money")

        except Address.DoesNotExist:
            raise PermissionDenied('This address is not found or not belongs to this user.')

        return Response("OK", status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        client = get_rpc_client(host=settings.ETHNODE_URL)

        address = Address(owner=request.user)
        address.key = random_string()

        password = self.get_address_password(key=address.key)
        address.address = client.personal_newAccount(password=password)
        address.save()

        serializer = self.get_serializer(address)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
