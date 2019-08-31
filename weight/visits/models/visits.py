"""Visits model."""

# Django
from django.db import models

# Utilities
from weight.utils.models import WeightModel, VisitItems

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
        return 'patient:{} visited Doctor: {} for: {}'.format(
            self.patient,
            self.doctor,
            self.type_visit
        )


class FirstVisitComplementInformation(WeightModel, VisitItems):
    """"First Visit Complement information."""

    visit = models.OneToOneField(
        'Visit',
        on_delete=models.CASCADE
    )




# class VisitInformation(models.Model):
#     """Visit informations.

#     Criteries that doctor collect about patient.
#     """

#     slugname = models.SlugField(
#         'Slugname de Criterio',
#         unique=True,
#         max_length=40
#     )

#     title = models.CharField(
#         'Titulo de criterio',
#         max_length=500
#     )

#     is_active_first_visit = models.BooleanField(
#         'Es Activo para primera visita',
#         help_text='Active item for first visit.',
#         default=True
#     )

#     is_active_follow_up_visit = models.BooleanField(
#         'Es Activo para visita de seguimiento',
#         help_text='Active item for follow-up visit.',
#         default=True
#     )

#     class Meta:
#         """Meta class."""

#         verbose_name = 'Informacion de Visita'
#         verbose_name_plural = 'Informacion de Visitas'

#     def __str__(self):
#         """Return visit info."""
#         return '@slugname:{} - Title: {}'.format(
#             self.slugname,
#             self.title,
#         )


