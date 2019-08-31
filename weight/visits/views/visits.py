"""Visits views."""

# Django Rest Framework
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

# Permissions
from rest_framework.permissions import IsAuthenticated
from weight.patients.permissions import IsDoctorPatient

# Models
from weight.patients.models import Patient
from weight.visits.models import Visit

# Serializers
from weight.visits.serializers import (
    VisitModelSerializer,
    CreateVisitModelModelSerializer)


class VisitViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    """Visit view set."""

    def dispatch(self, request, *args, **kwargs):
        """Verify that the patient exists."""
        self.username = kwargs['username']
        self.patient = get_object_or_404(Patient, username=self.username)
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == 'create':
            return CreateVisitModelModelSerializer
        return VisitModelSerializer

    def get_permissions(self):
        """Assign permission based on action."""
        permissions = [IsAuthenticated, IsDoctorPatient]
        return [p() for p in permissions]

    def get_queryset(self):
        """Return member visits."""
        return Visit.objects.filter(
            patient=self.patient
        )

    def get_serializer_context(self):
        """Add patient to a serializer context."""
        context = super().get_serializer_context()
        context['patient'] = self.patient
        return context

    def create(self, request, *args, **kwargs):
        """Custom create method."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        visit, result = serializer.save()
        response_data = VisitModelSerializer(visit).data
        response_data['result'] = result
        return Response(response_data, status=status.HTTP_201_CREATED)
