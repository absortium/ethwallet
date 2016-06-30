from ethwallet.celery import tasks

__author__ = 'andrew.shvv@gmail.com'

from django.conf import settings
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.utils.logging import getPrettyLogger
from ethwallet.models import Address
from ethwallet.rpc import get_rpc_client
from ethwallet.serializer.serializers import AddressSerializer
from ethwallet.utils import get_wallet_password, eth2wei

logger = getPrettyLogger(__name__)


def create_address(user, base_address=False):
    client = get_rpc_client(host=settings.ETHNODE_URL)

    password = get_wallet_password(user.wallet_secret_key)

    address = Address(owner=user, is_base_address=base_address)

    address.address = client.personal_newAccount(password=password)
    address.save()

    return address


class AddressViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = AddressSerializer

    def get_queryset(self):
        return self.request.user.addresses.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(create_address(request.user))
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


@api_view(http_method_names=['POST'])
def send(request, *args, **kwargs):
    to_address = request.data.get('address')
    if not to_address:
        raise ValidationError("'address' field is not specified")

    amount = request.data.get('amount')
    if not amount:
        raise ValidationError("'amount' field is not specified")

    try:
        amount = int(amount)
    except ValueError:
        raise ValidationError("'amount' field should be 'int' deserializable")

    base_address = Address.objects.get(is_base_address=True, owner_id=request.user.pk)

    context = {
        'user_pk': request.user.pk,
        'from_address': base_address.address,
        'to_address': to_address,
        'value': amount
    }

    async_result = tasks.send.delay(**context)
    obj = async_result.get(propagate=True)
    return Response(obj, status=status.HTTP_200_OK)
