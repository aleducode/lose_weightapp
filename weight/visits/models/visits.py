"""Visits model."""

# Django
from django.db import models

# Utilities
from weight.utils.models import WeightModel

VISIT_TYPE_CHOICES = [
    ('First', 'First'),
    ('Follow-Up', 'Follow-Up'),
]


class Visit(WeightModel):
    """Visits model.

    visits are entities that store the information that
    doctor register for each revision to patient.
    """

    doctor = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='rated_ride'
    )

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
    )

    weight = models.FloatField(
        'Current patient weight',
        max_length=5
    )

    height = models.FloatField(
        'Current patient height',
        max_length=6,
        blank=True,
        null=True
    )

    type_visit = models.CharField(
        'Visit Type',
        max_length=10,
        choices=VISIT_TYPE_CHOICES,
    )

    risk_factor = models.BooleanField(
        'Risk factor',
        null=False,
        blank=False,
        help_text='Risk factor item'
    )

    class Meta:
        """Meta class."""

        verbose_name = 'Visita'
        verbose_name_plural = 'Visitas'

    def __str__(self):
        """Return visit info."""
        return 'patient:{} visited doctor: {}'.format(
            self.patient,
            self.doctor,
        )
