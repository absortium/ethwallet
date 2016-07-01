__author__ = 'andrew.shvv@gmail.com'

from django.apps import AppConfig


class EthWalletConfig(AppConfig):
    name = 'ethwallet'
    verbose_name = "Ethwallet"

    def ready(self):
        super(EthWalletConfig, self).ready()

        from ethwallet import signals

        from django.conf import settings
        if settings.MODE in ['frontend', 'integration']:
            """
                Because celery run in another process we should manually mock
                what we need when we test celery in integration mode.
            """

            if settings.MODE == 'integration':
                from ethwallet.tests.mixins.celery import CeleryMockMixin
                CeleryMockMixin().mock_celery()

            from ethwallet.tests.mixins.notification import NotificationMockMixin
            NotificationMockMixin().mock_notification()
