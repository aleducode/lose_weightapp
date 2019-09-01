"""Visits views."""

# Django Rest Framework
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

# Permissions
from rest_framework.permissions import IsAuthenticated
from weight.patients.permissions import IsDoctorPatient

# Models
from weight.patients.models import Patient
from weight.visits.models import (
    Visit,
    FirstVisitComplementInformation,
    FollowUpVisitComplementInformation
)

# Serializers
from weight.visits.serializers import (
    VisitModelSerializer,
    CreateVisitModelModelSerializer,
    FirstVisitComplementSerializer,
    FollowUpVisitComplementSerializer
)


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
        elif self.action == 'complement_first':
            return FirstVisitComplementSerializer
        elif self.action == 'complement_follow_up':
            return FollowUpVisitComplementSerializer
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
        # Try for redoc and swagger issue
        try:
            context['patient'] = self.patient
        except:
            pass
        return context

    def create(self, request, *args, **kwargs):
        """Custom create method."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        visit = serializer.save()
        response_data = VisitModelSerializer(visit).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def complement_first(self, request, *args, **kwargs):
        """Anaylze patient data to generate medical concept."""
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            data=request.data,
            context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        visit = serializer.save()
        data = VisitModelSerializer(visit).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def complement_follow_up(self, request, *args, **kwargs):
        """Anaylze patient data to generate medical concept for follow up visit."""
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            data=request.data,
            context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        visit = serializer.save()
        data = VisitModelSerializer(visit).data
        return Response(data, status=status.HTTP_201_CREATED)
    