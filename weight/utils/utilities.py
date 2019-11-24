"""Utilities project."""

# Django
from django.utils import timezone
from django.conf import settings

# utils
from datetime import datetime, timedelta
import jwt


def generate_auth_token(user, token_usage):
    """Create JWT token that the user can use to login."""
    expiration_date = timezone.localtime() + timedelta(minutes=5)
    payload = {
        'user': user.username,
        # UTC format
        'exp': int(expiration_date.timestamp()),
        'type': token_usage
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token.decode()