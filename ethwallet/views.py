__author__ = 'andrew.shvv@gmail.com'
import binascii
import hashlib

from django.conf import settings
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from core.utils.logging import getPrettyLogger
from ethwallet.model.models import Address
from ethwallet.serializer.serializers import AddressSerializer

logger = getPrettyLogger(__name__)
from ethwallet.rpc import get_rpc_client


class AddressViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):

    serializer_class = AddressSerializer

    def get_queryset(self):
        return self.request.user.addresses.all()

    def get_address_password(self, user):
        salt = settings.SECRET_KEY.encode()
        password = user.password.encode()
        dk = hashlib.pbkdf2_hmac('sha256', password=password, salt=salt, iterations=100000)
        return binascii.hexlify(dk).decode()

    @detail_route(methods=['post'])
    def send(self, pk):
        client = get_rpc_client()
        password = self.get_address_password(self.request.user)
        address = self.get_object()
        # client.eth_sendTransaction(from_address=address.address, to_address=, password=password)

    def create(self, request, *args, **kwargs):
        client = get_rpc_client()
        password = self.get_address_password(self.request.user)
        address = client.personal_newAccount(password=password)

        address = Address(address=address, owner=request.user)
        address.save()

        serializer = self.get_serializer(address)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
