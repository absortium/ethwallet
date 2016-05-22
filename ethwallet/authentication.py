import hashlib
import hmac

__author__ = 'andrew.shvv@gmail.com'

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from core.utils.logging import getPrettyLogger

logger = getPrettyLogger(__name__)


class APIKeyAuth(BaseAuthentication):
    def authenticate(self, request):
        logger.debug(request)
        logger.debug(request.META)
        if 'HTTP_ETHWALLET_ACCESS_KEY' not in request.META:
            return None

        if 'HTTP_ETHWALLET_ACCESS_SIGN' not in request.META:
            return None

        if 'HTTP_ETHWALLET_ACCESS_TIMESTAMP' not in request.META:
            return None

        if 'HTTP_ETHWALLET_VERSION' not in request.META:
            return None

        key = request.META['HTTP_ETHWALLET_ACCESS_KEY']
        recv_signature = request.META['HTTP_ETHWALLET_ACCESS_SIGN']
        timestamp = request.META['HTTP_ETHWALLET_ACCESS_TIMESTAMP']

        data = request.body

        # TODO: Create linked model that will store key,secret,user_id
        User = get_user_model()

        logger.debug([key, recv_signature, timestamp])
        try:
            logger.debug([user.api_key for user in User.objects.all()])
            user = User.objects.get(api_key=key)
        except User.DoesNotExist:
            return None, None

        gen_signature = hmac.new(user.api_secret.encode(), data, hashlib.sha256).hexdigest()
        if recv_signature == gen_signature:
            return user, None
        else:
            raise PermissionDenied("Non-valid signature was specified")
