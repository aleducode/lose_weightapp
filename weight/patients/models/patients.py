"""Patients model."""

# Django
from django.db import models

# Utils
from weight.utils.models import WeightModel
import datetime

GENDER_CHOICES = [
        ('M', 'M'),
        ('F', 'F'),
    ]


class Patient(WeightModel):
    """Patients model."""

    first_name = models.CharField(
        'Nombre Paciente',
        max_length=140
        )

    last_name = models.CharField(
        'Apellido Paciente',
        max_length=140
        )
    username = models.SlugField(
        'Nombre de Usuario Paciente',
        unique=True,
        max_length=15
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

    def age(self):
        """Return age for patient."""
        age = round(int((datetime.date.today() - self.birthdate).days)/365, 0)
        return age

    def __str__(self):
        """Return name."""
        return self.username

    def get_short_name(self):
        """Return name."""
        return self.username
        
