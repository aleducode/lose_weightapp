"""Visit models admin."""

# Django
from django.contrib import admin

# Models
from weight.visits.models import (
    Visit,
    FirstVisitComplementInformation
)

admin.site.register(Visit)
admin.site.register(FirstVisitComplementInformation)
