# import absolute imports from the future, so that our celery.py module
# will not clash with the library

from __future__ import absolute_import

from ethwallet.celery.app import app as celery_app

default_app_config = 'ethwallet.apps.EthWalletConfig'

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
