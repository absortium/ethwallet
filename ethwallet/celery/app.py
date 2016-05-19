from __future__ import absolute_import

__author__ = 'andrew.shvv@gmail.com'

import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ethwallet.settings')

from core.utils.logging import getPrettyLogger

logger = getPrettyLogger(__name__)

app = Celery('ethwallet',
             broker=settings.CELERY_BROKER,
             backend=settings.CELERY_RESULT_BACKEND)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
