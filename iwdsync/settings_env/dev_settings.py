"""iwdsync/settings_env/dev_settings.py
"""
import os
from decouple import config


DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALLOWED_HOSTS = ["localhost"]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'PASSWORD': config('DB_PASS'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

CORS_ORIGIN_WHITELIST = ['http://localhost:3000']
CSRF_TRUSTED_ORIGINS = ['localhost:3000', 'localhost:8000']
CORS_ALLOW_CREDENTIALS = True
