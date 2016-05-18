"""
Django settings for ethwallet project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import sys
from datetime import timedelta

docker_environments = {
    'SECRET_KEY': 'DJANGO_SECRET_KEY',
    'WHOAMI': 'WHOAMI',
    'POSTGRES_PASSWORD': 'POSTGRES_PASSWORD',
}

settings_module = sys.modules[__name__]
for name, env_name in docker_environments.items():
    value = os.environ[env_name] if env_name in os.environ else None
    setattr(settings_module, name, value)

CELERY_TEST = False
CELERY_BROKER = 'amqp://guest@docker.celery.broker//'
CELERY_RESULT_BACKEND = 'redis://docker.celery.backend'

CELERYBEAT_SCHEDULE = {
    'check_block-every-10-seconds': {
        'task': 'tasks.check_block',
        'schedule': timedelta(seconds=10)
    },
}

CELERY_TIMEZONE = 'UTC'

ROUTER_URL = "http://docker.router:8080/publish"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_extensions',
    'rest_framework',
    'ethwallet',
    'ethwallet.celery',
]

AUTH_USER_MODEL = "ethwallet.ClientUser"
ETHNODE_URL = "docker.ethnode"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'ethwallet.authentication.APIKeyAuth',
    ),
    'PAGE_SIZE': 10,
}

ROOT_URLCONF = 'ethwallet.urls'
WSGI_APPLICATION = 'wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ethwallet',
        'USER': 'postgres',
        'PASSWORD': getattr(settings_module, 'POSTGRES_PASSWORD'),
        'HOST': 'docker.postgres',
        'PORT': '5432',
        'CONN_MAX_AGE': 500
    }
}

SILENCED_SYSTEM_CHECKS = ["models.W001"]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
