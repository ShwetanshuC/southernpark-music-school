from __future__ import annotations

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") not in {"0", "false", "False"}

_ALLOWED = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = (
    [h.strip() for h in _ALLOWED.split(",") if h.strip()]
    if _ALLOWED
    else (["*"] if DEBUG else ["southernparkmusicschool.com", "www.southernparkmusicschool.com", "localhost", "127.0.0.1"])
)

# Production security settings (only when DEBUG=False)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "SAMEORIGIN"  # needed for CKEditor iframes

CSRF_TRUSTED_ORIGINS = [
    "https://southernparkmusicschool.com",
    "https://www.southernparkmusicschool.com",
    "https://*.amazonlightsail.com",
    "http://localhost",
    "http://127.0.0.1",
]

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",
    "sitecontent.apps.SitecontentConfig",
    "pages",
    "faculty",
    "gallery",
    "policies",
    "image_cropping",
    "easy_thumbnails",
    "colorfield",
    "django_ckeditor_5", # Rich text editor for policies
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
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
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

# CKEditor 5 Configuration with Dark UI Theme
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|", "bold", "italic", "underline", "strikethrough", "bulletedList", "numberedList",
            "|", "outdent", "indent", "|", "link", "blockQuote", "insertTable", "|",
            "sourceEditing", "removeFormat", "undo", "redo"
        ],
        "height": 300,
        "width": "100%",
    },
    "minimal": {
        "toolbar": ["bold", "italic", "underline", "link", "|", "sourceEditing", "removeFormat"],
        "height": 100,
        "width": "100%",
    },
}
CKEDITOR_5_FILE_STORAGE = STORAGES["default"]["BACKEND"]
CKEDITOR_5_UPLOAD_FILE_VIEW_NAME = "ckeditor_5_upload_file"

# Speed Optimization: Aggressive caching for Lightsail
WHITENOISE_MAX_AGE = 31536000  # 1 year
WHITENOISE_AUTOREFRESH = DEBUG  # re-read files in dev, skip in prod

# Thumbnail cache — avoid regenerating on every request
THUMBNAIL_CACHE_DIMENSIONS = True
THUMBNAIL_OPTIMIZE_COMMAND = {
    "jpeg": "/bin/true",  # skip if no optimizer installed; set to jpegoptim path if available
    "png": "/bin/true",
}

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
