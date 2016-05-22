__author__ = 'andrew.shvv@gmail.com'

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.utils.logging import getPrettyLogger
from ethwallet.utils import generate_token

logger = getPrettyLogger(__name__)


class ClientUser(AbstractUser):
    api_key = models.CharField(max_length=40, default=generate_token)
    api_secret = models.CharField(max_length=40, default=generate_token)
    webhook = models.CharField(max_length=40)


class Address(models.Model):
    address = models.CharField(max_length=50)

    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="addresses")
    key = models.TextField()

    class Meta():
        unique_together = ('address',)

    def update(self, **kwargs):
        # update() is converted directly to an SQL statement; it doesn't exec save() on the model
        # instances, and so the pre_save and post_save signals aren't emitted.
        Address.objects.filter(pk=self.pk).update(**kwargs)


class Transaction(models.Model):
    from_address = models.CharField(max_length=50)
    to_address = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=30, decimal_places=1)
    block_number = models.IntegerField()
    owner = models.ForeignKey(Address, related_name="transactions")
    notified = models.BooleanField(default=False)
    hash = models.CharField(max_length=100)

    class Meta():
        unique_together = ('hash',)


class Block(models.Model):
    number = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    hash = models.CharField(max_length=100)

    class Meta():
        unique_together = ('hash',)
