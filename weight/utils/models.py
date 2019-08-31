"""Django models utilities."""

# Django
from django.db import models

INSUFICIENCIA_CHOICES = [
    ('No', 'No'),
    ('Leve', 'Leve'),
    ('Moderada', 'Moderada a grave'),
]

ACTIVIDAD_FISICA_CHOICES = [
    ('uno-dos', '1-2 veces por semana'),
    ('tres-mas', '3 o mas veces por semana'),
]


class WeightModel(models.Model):
    """Weight base model.

    WeightModel acts as an abstract base class from which every
    other model in the project will inherit. This class provides
    every table with the following attributes:
        + created (DateTime): Store the datetime the object was created.
        + modified (DateTime): Store the last datetime the object was modified.
    """

    created = models.DateTimeField(
        'created at',
        auto_now_add=True,
        help_text='Date time on which the object was created.'
    )
    modified = models.DateTimeField(
        'modified at',
        auto_now=True,
        help_text='Date time on which the object was last modified.'
    )

    class Meta:
        """Meta option."""

        # Does not show in db
        abstract = True

        get_latest_by = 'created'
        ordering = ['-created', '-modified']


class VisitItems(models.Model):
    """Visit questions.

    The patient can have two types of visits [first, follow-up]
    and the common questions in there will be inheritanced from 
    this model.
    """

    depresion_mayor = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    otros_transtornos = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    hta_no_controlada = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    tratamiento_hipoglucemiantes = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    convulsiones = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    factores_predisponentes = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    anorexia = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    abuso_alcohol = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    tratamiento_actual = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    alergia_naltrexona = models.BooleanField(
        default=False,
        help_text='item for visit'
    )
    
    embarazo = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    insuficiencia_hepatica = models.CharField(
        'Visit Type',
        max_length=10,
        choices=INSUFICIENCIA_CHOICES,
    )

    glaucoma = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    tratamiento_beta_bloqueantes = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    actividad_fisica = models.CharField(
        'Visit Type',
        max_length=10,
        choices=ACTIVIDAD_FISICA_CHOICES,
    )

    dieta_hipocalorica = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    funcion_renal = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    papitaciones_aumento_fc = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    tratamiento_levodopa = models.BooleanField(
        default=False,
        help_text='item for visit'
    )
    intolerancia_lactosa = models.BooleanField(
        default=False,
        help_text='item for visit'
    )

    class Meta:
        """Meta option."""

        # Does not show in db
        abstract = True
