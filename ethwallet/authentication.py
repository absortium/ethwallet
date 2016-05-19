import hashlib
import hmac
import json

__author__ = 'andrew.shvv@gmail.com'

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from core.utils.logging import getPrettyLogger

logger = getPrettyLogger(__name__)


class APIKeyAuth(BaseAuthentication):
    def authenticate(self, request):
        if 'ETHWALLET-ACCESS-KEY' not in request.META:
            return None

        if 'ETHWALLET-ACCESS-SIGN' not in request.META:
            return None

        if 'ETHWALLET-ACCESS-TIMESTAMP' not in request.META:
            return None

        if 'ETHWALLET-VERSION' not in request.META:
            return None

        key = request.META['ETHWALLET-ACCESS-KEY']
        signature = request.META['ETHWALLET-ACCESS-SIGN']
        timestamp = request.META['ETHWALLET-ACCESS-TIMESTAMP']

        data = request.body

        User = get_user_model()
        user = User.objects.get(api_key=key)

        s = hmac.new(user.api_secret.encode(), data, hashlib.sha256).hexdigest()

        logger.debug({
            'data': data,
            'api_secret': user.api_secret.encode(),
            'gen signature': s,
            'rec signature': signature
        })

        return user, None

        #
        # if signature == hmac.new(user.api_secret.encode(), message.encode(), hashlib.sha256).hexdigest():
        #     return user, None
        # else:
        #     raise PermissionDenied("Non-valid signature was specified")
