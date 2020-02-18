"""
Django 3.0

"""

import os
import sys

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

# Retrieve settings from environment
# props go to Shabeer Ayar https://medium.com/@ayarshabeer/django-best-practice-settings-file-for-multiple-environments-6d71c6966ee2


def get_env_var(setting):
    try:
        val = os.environ[setting]
        return val
    except KeyError:
        error_msg = "ImproperlyConfigured: Set {0} environment variable".format(
            setting)
        raise ImproperlyConfigured(error_msg)


# General settings

TESTING = False

DEBUG = True

X_FRAME_OPTIONS = 'SAMEORIGIN'

TEST_RUNNER = 'core.tests.runners.MyTestSuiteRunner'

SECRET_KEY = get_env_var('SECRET_KEY')

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

PROJECT_DIR = os.path.join(BASE_DIR, 'resource_hub')

ALLOWED_HOSTS = []

ROOT_URLCONF = 'resource_hub.urls'

WSGI_APPLICATION = 'resource_hub.wsgi.application'
ASGI_APPLICATION = 'resource_hub.asgi.application'

MAP_API_TOKEN = get_env_var('MAP_API_TOKEN')
GITLAB_TOKEN = get_env_var('GITLAB_TOKEN')


# Application definition

INSTALLED_APPS = [
    # native apps
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third party
    'django_extensions',
    'django_tables2',
    'django_rq',
    'django_summernote',
    'imagekit',
    'recurrence',
    'rest_framework',
    'sekizai',
    # project apps
    'core.apps.CoreConfig',
    'core.apps.ControlConfig',
    'core.apps.ApiConfig',
    'plugins.bank_transfer.BankTransfer',
    'venues.apps.VenuesConfig',
]

MIDDLEWARE = [
    # native middleware
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # custom middleware
    'core.middleware.ActorMiddleware',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # custom preprocessors
                'sekizai.context_processors.sekizai',

                'core.context_processors.actor',
                'core.context_processors.map_api_token',
            ],
        },
    },
]


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Database

DATABASES = {
    'default': {
        'ENGINE': get_env_var('DB_ENGINE'),
        'NAME': get_env_var('DB_NAME'),
        'USER': get_env_var('DB_USER'),
        'PASSWORD': get_env_var('DB_PW'),
        'HOST': get_env_var('DB_HOST'),
        'PORT': get_env_var('DB_PORT'),
    }
}


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = get_env_var('TIMEZONE')

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    (('en'), _('English')),
    (('de'), _('Deutsch')),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'locale'),
)


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
MEDIA_URL = '/media/'


# Custom settings

LOGIN_REDIRECT_URL = 'control:home'
LOGIN_URL = 'core:login'

AUTH_USER_MODEL = "core.User"


# django REST plugin settings

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}


# caching settings

CACHES = {
    "default": {
        "BACKEND": 'django_redis.cache.RedisCache',
        "LOCATION": get_env_var('REDIS_LOCATION'),
        "KEY_PREFIX": get_env_var("REDIS_KEY_PREFIX"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
CACHE_TTL = 60 * 15


# redis queue

RQ_QUEUES = {
    'high': {
        'USE_REDIS_CACHE': 'default',
    },
    'low': {
        'USE_REDIS_CACHE': 'default',
    },
    'default': {
        'USE_REDIS_CACHE': 'default',
    },
}


# summernote

SUMMERNOTE_THEME = 'lite'
SUMMERNOTE_CONFIG = {
    'iframe': True,
    'summernote': {
        'airMode': False,

        'width': '100%',
        'height': '480',
    },

    'css': (
        '/static/css/summernote.css',
    ),
}
