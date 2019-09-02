"""Visits model."""

# Django
from django.db import models

# Utilities
from weight.utils.models import (
    WeightModel,
    VisitItems,
    FUNCION_RENAL_CHOICES)

VISIT_TYPE_CHOICES = [
    ('first', 'First'),
    ('follow-up', 'Follow-Up'),
]

INSUFICIENCIA_CHOICES = [
    ('no', 'No'),
    ('leve', 'Leve'),
    ('moderada', 'Moderada a grave'),
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
    concept = models.CharField(
        'Concepto final visita',
        null=True,
        blank=True,
        max_length=130
    )
    result = models.TextField(
        'Resultado de visita',
        null=True,
        blank=True,
        default=""
    )
    result_header = models.TextField(
        'Encabezado de visita',
        null=True,
        blank=True,
        default=""
    )
    treatment_weaks = models.CharField(
        'Semanas de tratamiento',
        null=True,
        blank=True,
        max_length=2,
        default=""
    )
    percentage_evolution = models.CharField(
        'Porcentaje de evolución del peso',
        null=True,
        blank=True,
        max_length=4,
        default=""
    )

    class Meta:
        """Meta class."""

        verbose_name = 'Visita'
        verbose_name_plural = 'Visitas'

    def __str__(self):
        """Return visit info."""
        return 'Patient: {} visited Doctor: {}. for: {}'.format(
            self.patient.first_name,
            self.doctor,
            self.type_visit,
        )


class FirstVisitComplementInformation(WeightModel, VisitItems):
    """"First Visit Complement information."""

    visit = models.OneToOneField(
        'Visit',
        on_delete=models.CASCADE
    )

    funcion_renal = models.CharField(
        'Funcion Renal',
        max_length=50,
        choices=FUNCION_RENAL_CHOICES,
    )

    alergia_naltrexona = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    insuficiencia_hepatica = models.CharField(
        'Insuficiencia hepatica',
        max_length=10,
        choices=INSUFICIENCIA_CHOICES,
    )


    class Meta:
        """Meta class."""

        verbose_name = 'Complemento Primera Visita'
        verbose_name_plural = 'Complementos para Primeras Visitas'

    def __str__(self):
        """Return visit info."""
        return str(self.visit)


class FollowUpVisitComplementInformation(WeightModel, VisitItems):
    """"FollowUp Visit Complement information."""

    visit = models.OneToOneField(
        'Visit',
        on_delete=models.CASCADE
    )
    hepatitis_aguda = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    hipertension_arterial = models.BooleanField(
        default=False,
        help_text='item for visit'
    )
    disfuncion_renal = models.CharField(
        'Disfuncion Renal',
        max_length=50,
        choices=FUNCION_RENAL_CHOICES,
    )

    nauseas = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    constipacion = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    cefalea = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    mareos = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    insomnio = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    boca_seca = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    diarrea = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    vomitos = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    dolor_abdominal = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    otros_eventos = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    incio_tratamiento_actual = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    suspendio = models.BooleanField(
        default=False,
        help_text='item for visit'
    )


    class Meta:
        """Meta class."""

        verbose_name = 'Complemento Visita Seguimiento'
        verbose_name_plural = 'Complementos para Visitas de Seguimiento'

    def __str__(self):
        """Return visit info."""
        return str(self.visit)

