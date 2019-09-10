from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = get_env_var('ALLOWED_HOSTS')

STATIC_ROOT = get_env_var('STATIC_ROOT')
MEDIA_ROOT = get_env_var('MEDIA_ROOT')

# SMTP Server settings
EMAIL_USE_TLS = get_env_var('EMAIL_USE_TLS')
EMAIL_HOST = get_env_var('EMAIL_HOST')
EMAIL_HOST_USER = get_env_var('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_var('EMAIL_HOST_PASSWORD')
EMAIL_PORT = get_env_var('EMAIL_PORT')
DEFAULT_FROM_EMAIL = get_env_var('DEFAULT_FROM_EMAIL')
