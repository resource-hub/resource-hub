from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# SMTP Server settings
EMAIL_USE_TLS = get_env_var('EMAIL_USE_TLS')
EMAIL_HOST = get_env_var('EMAIL_HOST')
EMAIL_HOST_USER = get_env_var('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_var('EMAIL_HOST_PASSWORD')
EMAIL_PORT = get_env_var('EMAIL_PORT')
DEFAULT_FROM_EMAIL = get_env_var('DEFAULT_FROM_EMAIL')
