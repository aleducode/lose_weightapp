"""Patients models admin."""

# Django
from django.contrib import admin
from django.http import HttpResponse

# Models
from weight.patients.models import (
    Patient
)

# Utilities
import csv


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Patient model admin."""

    list_display = ('first_name', 'username', 'doctor', 'gender')
    search_fields = ('first_name', 'first_name', 'doctor__username', 'doctor__first_name')
    actions = ['download_patients']

    def download_patients(self, request, queryset):
        """Return all patients ."""
        patients = Patient.objects.filter(
            pk__in=queryset.values_list('pk'),
        ).order_by('-created')

        # Response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="allpatients.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'id',
            'name',
            'username',
            'doctor_username',
            'doctor_pk',
            'gender',
            'age',
            'created',
        ])
        for user in patients:
            writer.writerow([
                user.pk,
                user.get_full_name(),
                user.username,
                user.doctor.username,
                user.doctor.pk,
                user.gender,
                user.age(),
                user.created
            ])
        return response

    download_patients.short_description = 'Download selected patients'

