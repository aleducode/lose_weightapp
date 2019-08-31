"""Visit models admin."""

# Django
from django.contrib import admin

# Models
from weight.visits.models import (
    Visit
)

admin.site.register(Visit)
