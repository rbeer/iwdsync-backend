"""iwdsync/settings_env/dev_settings.py
"""
import os
from decouple import config, Csv

DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# use e.g. Redis here in production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

CORS_ORIGIN_ALLOW_ALL = False

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost',
    cast=Csv()
)

CORS_ORIGIN_WHITELIST = config(
    'CORS_ORIGIN_WHITELIST',
    default='http://localhost:3000',
    cast=Csv()
)
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='localhost:3000, localhost:8000',
    cast=Csv()
)
CORS_ALLOW_CREDENTIALS = config(
    'CORS_ALLOW_CREDENTIALS',
    default=True,
    cast=bool
)
