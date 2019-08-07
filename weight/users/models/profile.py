"""Profile model."""

# Django
from django.db import models

# utilities
from weight.utils.models import WeightModel


class RegistrationType(models.Model):
    """Doctor's Registration type."""

    name = models.CharField(
        'Name Registration type',
        max_length=250,
    )

    def __str__(self):
        """return registration type name"""
        return str(self.name)


class Profile(WeightModel):
    """Profile model.

    a profile holds a users public data
    """

    user = models.OneToOneField('users.User', on_delete=models.CASCADE)

    specialty = models.CharField(
        'Speciality',
        max_length=500,
        blank=True,
        null=True
    )
    registration_type = models.ForeignKey(
        RegistrationType,
        on_delete=models.CASCADE,
        help_text='Registration type of each doctor.'
    )
    registration_number = models.CharField(
        'Registration Number',
        max_length=20,
    )

    def __str__(self):
        """return users name"""
        return str(self.user)


