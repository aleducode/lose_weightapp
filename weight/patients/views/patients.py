"""Patients views."""

# Django Rest Framework
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

# Permissions
from rest_framework.permissions import IsAuthenticated
from weight.patients.permissions import IsDoctorPatient

# Models
from weight.patients.models import Patient

# Serializers
from weight.patients.serializers import (
    PatientModelSerializer,
    CreatePatientModelSerializer)


class PatientViewSet(mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    """Patient view set."""

    queryset = Patient.objects.all()
    lookup_field = 'document'

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == 'create':
            return CreatePatientModelSerializer
        return PatientModelSerializer

    def get_permissions(self):
        """Assign permission based on action."""
        permissions = [IsAuthenticated]
        if self.action in ['retrieve']:
            permissions.append(IsDoctorPatient)
        return [p() for p in permissions]