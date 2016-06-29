from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from core.utils.logging import getPrettyLogger
from ethwallet.utils import generate_token
from ethwallet.views import create_address

__author__ = 'andrew.shvv@gmail.com'

logger = getPrettyLogger(__name__)


@receiver(post_save, sender=get_user_model(), dispatch_uid="user_post_save")
def user_post_save(sender, instance, *args, **kwargs):
    user = instance

    user.wallet_secret_key = generate_token()
    create_address(user, base_address=True)
