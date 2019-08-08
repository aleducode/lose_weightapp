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

    class Meta:
        """Meta class."""

        verbose_name = 'Tipo de Matrícula'
        verbose_name_plural = 'Tipo de Matrículas'

    def __str__(self):
        """Return registration type name."""
        return str(self.name)


class Speciality(models.Model):
    """Doctor's Speciality type."""

    name = models.CharField(
        'Speciality Name',
        max_length=250,
    )

    class Meta:
        """Meta class."""

        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'

    def __str__(self):
        """Return speciality type name."""
        return str(self.name)


class Profile(WeightModel):
    """Profile model.

    a profile holds a users public data
    """

    user = models.OneToOneField('users.User', on_delete=models.CASCADE)

    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.CASCADE,
        help_text='Speciality of doctor.'
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

    class Meta:
        """Meta class."""

        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        """Return users name."""
        return str(self.user)


