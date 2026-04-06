from __future__ import annotations

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") not in {"0", "false", "False"}
ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://southernparkmusicschool.com",
    "https://www.southernparkmusicschool.com",
    "https://*.amazonlightsail.com",
    "http://localhost",
    "http://127.0.0.1",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",
    "sitecontent",
    "pages",
    "faculty",
    "gallery",
    "policies",
    "easy_thumbnails",
    "image_cropping",
    "colorfield",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "southernpark.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sitecontent.context_processors.site_settings",
            ],
        },
    }
]

WSGI_APPLICATION = "southernpark.wsgi.application"
ASGI_APPLICATION = "southernpark.asgi.application"

if os.environ.get("DB_NAME") and os.environ.get("DB_USER"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME"),
            "USER": os.environ.get("DB_USER"),
            "PASSWORD": os.environ.get("DB_PASSWORD"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
elif os.environ.get("DATABASE_URL"):
    DATABASES = {"default": dj_database_url.parse(os.environ.get("DATABASE_URL"), conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

# S3 media storage (used in production when S3 credentials are set)
_s3_bucket = os.environ.get("S3_AWS_STORAGE_BUCKET_NAME")
if _s3_bucket:
    AWS_ACCESS_KEY_ID = os.environ.get("S3_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_KEY")
    AWS_STORAGE_BUCKET_NAME = _s3_bucket
    AWS_S3_REGION_NAME = os.environ.get("AWS_REGION", "us-east-1")
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": os.environ.get("S3_ACCESS_KEY"),
            "secret_key": os.environ.get("S3_SECRET_KEY"),
            "bucket_name": _s3_bucket,
            "querystring_auth": False,
            "file_overwrite": False,
        },
    }

DATA_UPLOAD_MAX_MEMORY_SIZE = None

from easy_thumbnails.conf import Settings as thumbnail_settings
THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + thumbnail_settings.THUMBNAIL_PROCESSORS

IMAGE_CROPPING_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js'
IMAGE_CROPPING_THUMB_SIZE = (300, 300)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO")},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
    },
}
