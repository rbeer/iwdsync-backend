"""iwdsync/settings_env/heroku_settings.py
"""
import os
from decouple import config

DEBUG = False
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALLOWED_HOSTS = []


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

STATIC_ROOT = os.path.join(BASE_DIR, "static")
