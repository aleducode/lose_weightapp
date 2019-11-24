from .base import *  # noqa
from .base import env

# GENERAL
DEBUG = True

# Security
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="fpiZXqBd6ZLx1d5rNG8lJCRDfd1x1cibaHSgJncbQp7J56zs2ktL0Lq013Y8C1uh",
)

ALLOWED_HOSTS = [
    "localhost",
    "0.0.0.0",
    "127.0.0.1",
    'idargentina.com']

# CACHES
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# EMAIL
EMAIL_BACKEND = env(
    'DJANGO_EMAIL_BACKEND', default='django_smtp_ssl.SSLEmailBackend'
)
EMAIL_TIMEOUT = 5
EMAIL_USE_TLS = True
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'AKIA2H62DLH3NBG6L2G5'
EMAIL_HOST_PASSWORD = 'BNd8R7sYQvNNo6HSlN8B0ZsnyYHZx+aVN3XytXRHeKri'
DEFAULT_FROM_EMAIL = 'noreply@jirafapp.com'


# django-extensions

INSTALLED_APPS += ["django_extensions"]  # noqa F405
