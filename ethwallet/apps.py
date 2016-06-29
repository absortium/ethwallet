__author__ = 'andrew.shvv@gmail.com'

from django.apps import AppConfig


class EthWalletConfig(AppConfig):
    name = 'ethwallet'
    verbose_name = "Ethwallet"

    def ready(self):
        super(EthWalletConfig, self).ready()

        from ethwallet import signals
        from django.conf import settings

        if settings.CELERY_TEST:
            """
                Because celery run in another process we should manually mock
                what we need when we test celery in integrity tests.
            """
            from ethwallet.tests.mixins.celery import CeleryMockMixin
            from ethwallet.tests.mixins.notification import NotificationMockMixin

            CeleryMockMixin().mock_celery()
            NotificationMockMixin().mock_notification()
