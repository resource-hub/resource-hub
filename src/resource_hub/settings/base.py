"""
Django 3.0

"""

import os
import sys

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

# Retrieve settings from environment
# props go to Shabeer Ayar https://medium.com/@ayarshabeer/django-best-practice-settings-file-for-multiple-environments-6d71c6966ee2


def get_env_var(setting, default=None):
    try:
        val = os.environ[setting]
        return val
    except KeyError:
        if default:
            return default
        error_msg = "ImproperlyConfigured: Set {0} environment variable".format(
            setting)
        raise ImproperlyConfigured(error_msg)


# General settings

TESTING = False

DEBUG = True

X_FRAME_OPTIONS = 'SAMEORIGIN'

TEST_RUNNER = 'resource_hub.core.tests.runners.MyTestSuiteRunner'

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

# site info
SITE_OWNER_NAME = get_env_var('SITE_OWNER_NAME', 'not configured')
SITE_OWNER_ADDRESS = get_env_var('SITE_OWNER_ADDRESS', 'not configured')
SITE_DOMAIN = get_env_var('SITE_DOMAIN', 'not.configured.com')
SITE_EMAIL = get_env_var('SITE_EMAIL', 'not@configured.com')


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
    'django_ical',
    'django_rq',
    'django_summernote',
    'django_tables2',
    'djangoformsetjs',
    'imagekit',
    'recurrence',
    'rest_framework',
    'sekizai',
    # project apps
    'resource_hub.core',
    'resource_hub.api',
    'resource_hub.control',
    'resource_hub.items',
    'resource_hub.plugins.bank_transfer',
    'resource_hub.plugins.sepa',
    'resource_hub.venues',
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
    'resource_hub.core.middleware.ActorMiddleware',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # custom preprocessors
                'sekizai.context_processors.sekizai',

                'resource_hub.core.context_processors.actor',
                'resource_hub.core.context_processors.map_api_token',
                'resource_hub.core.context_processors.contract_states',
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

DEFAULT_LANGUAGE = 'de'

DATETIME_INPUT_FORMATS = [
    '%d.%m.%Y %H:%M',
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%Y-%m-%d',              # '2006-10-25'
    '%m/%d/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
    '%m/%d/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
    '%m/%d/%Y %H:%M',        # '10/25/2006 14:30'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%y %H:%M:%S',     # '10/25/06 14:30:59'
    '%m/%d/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
    '%m/%d/%y %H:%M',        # '10/25/06 14:30'
    '%m/%d/%y',              # '10/25/06'
]

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, 'locale'),
)

CURRENCIES = [
    ('EUR', _('Euro (EUR)'))
]

CURRENCY_PLACES = {
    'EUR': 2,
    'USD': 2,
}

# has to be caps, for country field
DEFAULT_COUNTRY = 'DE'


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, "static"),
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
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 25,
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

# tables

DEFAULT_PER_PAGE = 25
MIN_PER_PAGE = 1
MAX_PER_PAGE = 1000

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
    'iframe': False,
    'disable_attachment': False,
    'summernote': {
        'airMode': False,

        'width': '100%',
        'height': '480',
    },

    'css': (
        '/static/css/summernote.css',
        '/static/css/summernote_dark.css',
    ),
}
