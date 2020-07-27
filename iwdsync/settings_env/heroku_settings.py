"""iwdsync/settings_env/heroku_settings.py
"""
import os
from decouple import config
import dj_database_url

DEBUG = False
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALLOWED_HOSTS = ['iwdsync.herokuapp.com']


DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)


STATIC_ROOT = os.path.join(BASE_DIR, "static")
