"""Visits model."""

# Django
from django.db import models

# Utilities
from weight.utils.models import WeightModel

VISIT_TYPE_CHOICES = [
    ('First', 'First'),
    ('Follow-Up', 'Follow-Up'),
]


# class VisitTerms(models.Model):
#     """Visit terms Model.

#     Store all items or questions to be used by doctor
#     in all visits.
#     """

#     title = models.CharField('Term title', max_length=140)
#     slug_name = models.SlugField(unique=True, max_length=100)

#     first_visit = models.BooleanField(
#         'Used first visit',
#         default=True,
#         help_text='Term is required for first visit.'
#     )
#     follow_up_visit = models.BooleanField(
#         'Used follow-up visit',
#         default=True,
#         help_text='Term is required for follow-up visit.'
#     )

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

    weight = models.CharField(
        'Current patient weight',
        max_length=5
    )

    height = models.CharField(
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
