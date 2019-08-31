"""Patients views."""

# Django Rest Framework
from rest_framework import viewsets, mixins, status
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
    lookup_field = 'username'

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

    def create(self, request, *args, **kwargs):
        """Custom create method."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = serializer.save()
        response_data = PatientModelSerializer(patient).data
        return Response(response_data, status=status.HTTP_201_CREATED)
