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
    "127.0.0.1"]

# CACHES
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# EMAIL
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}

# django-extensions

INSTALLED_APPS += ["django_extensions"]  # noqa F405
