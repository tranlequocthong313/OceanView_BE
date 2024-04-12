"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from dotenv import load_dotenv

load_dotenv()

import os
from pathlib import Path

import cloudinary
import pymysql

pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


ENVIRONMENT = os.environ.get("ENVIRONMENT", default="development")


def is_development_env():
    return ENVIRONMENT == "development"


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = is_development_env()

ALLOWED_HOSTS = [
    "0.0.0.0",
    "192.168.0.8",
    "192.168.1.176",
    "localhost",
    "127.0.0.1",
    "tranlequocthong313.pythonanywhere.com",
]


# Application definition

INSTALLED_APPS = [
    "user.apps.UserConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "oauth2_provider",
    "corsheaders",
    "invoice.apps.InvoiceConfig",
    "service.apps.ServiceConfig",
    "apartment.apps.ApartmentConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "user.middlewares.SendOTPRateLimitMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE"),
        "USER": os.environ.get("MYSQL_USER"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD"),
        "HOST": os.environ.get("MYSQL_HOST"),
        "PORT": os.environ.get("MYSQL_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

COMPANY_NAME = "OceanView"

AUTH_USER_MODEL = "user.User"

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

CORS_ALLOW_ALL_ORIGINS = is_development_env()

STATIC_ROOT = os.path.join(BASE_DIR, "static")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": [],
        },
    },
    "loggers": {
        logger_name: {"level": "WARNING", "propagate": True}
        for logger_name in (
            "django",
            "django.request",
            "django.db.backends",
            "django.template",
        )
    },
    "root": {"level": "DEBUG", "handlers": ["console"]},
}

LOGGING["formatters"]["colored"] = {
    "()": "colorlog.ColoredFormatter",
    "format": "%(log_color)s%(asctime)s %(levelname)s %(name)s %(bold_white)s%(message)s",
}
LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["handlers"]["console"]["formatter"] = "colored"

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": True,
    "SECURITY_DEFINITIONS": {
        "OceanView API - Swagger": {
            "type": "oauth2",
            "tokenUrl": "/o/token/",
            "flow": "password",
        }
    },
    "OAUTH2_CONFIG": {"clientId": CLIENT_ID, "appName": COMPANY_NAME},
}

TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")
TWILIO_SERVICE_SID = os.environ.get("TWILIO_SERVICE_SID")
TWILIO_SENDGRID_API_KEY = os.environ.get("TWILIO_SENDGRID_API_KEY")

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_BACKEND = "backend.email.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = f"{COMPANY_NAME} <{os.environ.get('EMAIL_HOST_USER')}>"

# I would have used Redis but since this project will be hosted on the Pythonaywhere trial
# and it does not allow communication protocols other than http(s) my temporary solution would
# be to use Database cache or maybe is FileBased cache. But I will switch to Redis when I can
# change the host platform
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

HASHING_SALT = os.environ.get("HASHING_SALT")

RESET_PASSWORD_TOKEN_EXPIRE_TIME = int(
    os.environ.get("RESET_PASSWORD_TOKEN_EXPIRE_TIME")
)
RATE_LIMIT_EXPIRE_TIME = 60

SPECTACULAR_SETTINGS = {
    "TITLE": "OceanView API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",  # shorthand to use the sidecar instead
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}
