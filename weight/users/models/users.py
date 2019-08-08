"""User model."""

# Django
from django.db import models
from django.contrib.auth.models import AbstractUser

# Utils
from weight.utils.models import WeightModel


class User(WeightModel, AbstractUser):
    """User model.

    Extend from Django abstract user, change the username field to email
    and add some extra info.
    """

    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': 'A user with that email already exist',
        }
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        """Meta class."""

        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        """Return username."""
        return self.username

    def get_short_name(self):
        """Return username."""
        return self.username