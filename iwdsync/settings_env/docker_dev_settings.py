"""iwdsync/settings_env/docker_dev_settings.py
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

# Redis django and session cache
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "cache"
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [{
                "address": f"{REDIS_URL}/1"
            }]
        }
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
