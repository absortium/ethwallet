from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.utils.logging import getPrettyLogger
from ethwallet import constants
from ethwallet.utils import generate_token

logger = getPrettyLogger(__name__)

__author__ = 'andrew.shvv@gmail.com'


class ClientUser(AbstractUser):
    api_key = models.CharField(max_length=constants.API_KEY_LEN, default=generate_token)
    api_secret = models.CharField(max_length=constants.API_SECRETS_LEN, default=generate_token)

    web_hook = models.TextField()
    wallet_secret_key = models.CharField(max_length=constants.WALLET_SECRET_KEY_LEN, default=generate_token)

    @property
    def base_address(self):
        return Address.objects.get(owner=self, is_base_address=True)


class Address(models.Model):
    address = models.CharField(max_length=constants.ADDRESS_LEN, primary_key=True)

    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="addresses")

    is_base_address = models.BooleanField(default=False)

    def update(self, **kwargs):
        # update() is converted directly to an SQL statement; it doesn't exec save() on the model
        # instances, and so the pre_save and post_save signals aren't emitted.
        Address.objects.filter(pk=self.pk).update(**kwargs)


class Transaction(models.Model):
    hash = models.CharField(max_length=constants.HASH_LEN, primary_key=True)

    from_address = models.CharField(max_length=constants.ADDRESS_LEN)
    to_address = models.CharField(max_length=constants.ADDRESS_LEN)

    value = models.DecimalField(max_digits=constants.MAX_DIGITS,
                                decimal_places=constants.DECIMAL_PLACES)
    spent = models.DecimalField(max_digits=constants.MAX_DIGITS,
                                decimal_places=constants.DECIMAL_PLACES,
                                default=0)
    block_number = models.IntegerField()

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="transactions")

    notification_status = models.IntegerField()
    redirected = models.BooleanField(default=False)

    @property
    def is_spent(self):
        return self.spent >= self.value


class Block(models.Model):
    hash = models.CharField(max_length=constants.HASH_LEN, primary_key=True)

    number = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
