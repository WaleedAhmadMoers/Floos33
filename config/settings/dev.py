"""Development settings."""

from .base import *

DEBUG = env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])
