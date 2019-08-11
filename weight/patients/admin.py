"""Patients models admin."""

# Django
from django.contrib import admin

# Models
from weight.patients.models import (
    Patient
)

admin.site.register(Patient)