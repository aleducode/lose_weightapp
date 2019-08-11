"""Patients model."""

# Django
from django.db import models

# Utils
from weight.utils.models import WeightModel

GENDER_CHOICES = [
        ('M', 'M'),
        ('F', 'F'),
    ]


class Patient(WeightModel):
    """Patients model."""

    name = models.CharField(
        'Nombre Paciente',
        max_length=140
        )
    document = models.SlugField(
        'Documento Paciente',
        unique=True,
        max_length=10
        )
    doctor = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE
    )
    gender = models.CharField(
        'Genero',
        max_length=2,
        choices=GENDER_CHOICES,
    )
    birthdate = models.DateField(
        'Fecha Nacimiento',
        auto_now=False,
        auto_now_add=False
    )

    class Meta:
        """Meta class."""

        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'

    def __str__(self):
        """Return name."""
        return self.name

    def get_short_name(self):
        """Return name."""
        return self.name