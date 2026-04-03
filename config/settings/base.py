"""Base Django settings shared across environments."""

import os
from pathlib import Path

from .env import env, env_bool, env_list, load_env

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", "change-this-secret-key")

DEBUG = env_bool("DJANGO_DEBUG", False)

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default=[])

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
]

LOCAL_APPS = [
    "accounts",
    "blog",
    "companies",
    "core",
    "stocklots",
    "inquiries",
    "rfqs",
    "channels",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

ASGI_APPLICATION = "config.asgi.application"

# Live layer: prefer Redis if REDIS_URL is provided; otherwise fall back to in-memory
REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
    }

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.cms_content",
                "core.context_processors.notifications",
                "core.context_processors.site_identity",
                "core.context_processors.ticker_news",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": env("SQLITE_NAME", str(BASE_DIR / "db.sqlite3")),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"

TIME_ZONE = env("DJANGO_TIME_ZONE", "Asia/Riyadh")

USE_I18N = False
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/account/dashboard/"
LOGOUT_REDIRECT_URL = "/"

EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", "smtp.ionos.de")
EMAIL_PORT = int(env("EMAIL_PORT", 587))
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "no-reply@floos33.de")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
EMAIL_TIMEOUT = int(env("EMAIL_TIMEOUT", 20))
EMAIL_FILE_PATH = env("DJANGO_EMAIL_FILE_PATH", str(BASE_DIR / "tmp" / "emails"))
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "no-reply@floos33.de")
SERVER_EMAIL = env("SERVER_EMAIL", DEFAULT_FROM_EMAIL)
SITE_NAME = env("DJANGO_SITE_NAME", "floos33")
SUPPORT_EMAIL = env("DJANGO_SUPPORT_EMAIL", "support@floos33.de")
SUPPORT_PHONE = "+49 1575 4967414"
FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", env("APP_BASE_URL", "http://127.0.0.1:8000")).rstrip("/")
APP_BASE_URL = FRONTEND_BASE_URL
ACCOUNT_EMAIL_VERIFICATION_REQUIRED = env_bool("ACCOUNT_EMAIL_VERIFICATION_REQUIRED", True)
ACCOUNT_SEND_WELCOME_EMAIL = env_bool("ACCOUNT_SEND_WELCOME_EMAIL", True)
PASSWORD_RESET_TIMEOUT = int(env("PASSWORD_RESET_TIMEOUT", 60 * 60 * 24 * 3))
