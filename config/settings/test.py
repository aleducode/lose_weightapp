"""Testing settings.

With these settings, tests run faster.
"""

from .base import *  # noqa
from .base import env

# GENERAL
DEBUG = False
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="nY2Z82jyFtSp4dNT7aOsXyCaiV3VvJt8eHOMFjuPVPdhW8rzJ7T6amlonnkfFl2p",
)
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# CACHES
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# PASSWORDS
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# TEMPLATES
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# Email
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025