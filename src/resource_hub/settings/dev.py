from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ev1&$r#j6x=4%(sb$j6sphnqy!3wmxsw9gt9h-m)2fus((#wtd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django',
        'USER': 'django',
        'PASSWORD': 'django',
        'HOST': 'postgres',
        'PORT': '',
    }
}

EMAIL_USE_TLS = True
EMAIL_HOST = 'webspace29.do.de'
EMAIL_HOST_USER = 'web71p9'
EMAIL_HOST_PASSWORD = 'zt8iFbBw'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'Test Server <server@ture.dev>'
