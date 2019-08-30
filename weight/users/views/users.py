"""Users views."""

# Django Rest Framework
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from weight.users.permissions import IsAccountOwner

# Serializers
from weight.users.serializers import (
    UserModelSerializer,
    UserLoginSerializer,
    UserSignUpSerializer
    )
from weight.patients.serializers import PatientModelSerializer

# Models
from weight.users.models import User
from weight.patients.models import Patient


class UserViewSet(mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """User view set.

    Handle login and signup.
    """

    queryset = User.objects.all()
    lookup_field = 'username'

    def get_permissions(self):
        """Assign permission based on action."""
        if self.action in ['signup', 'login']:
            permissions = [AllowAny]
        elif self.action in ['retrieve']:
            permissions = [IsAuthenticated, IsAccountOwner]
        elif self.action in ['patients']:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Return serializer based on action."""
        if self.action == 'login':
            return UserLoginSerializer
        if self.action == 'signup':
            return UserSignUpSerializer
        if self.action == 'patients':
            return PatientModelSerializer
        return UserModelSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login."""
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        data = {
            'user': UserModelSerializer(user).data,
            'access_token': token
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def signup(self, request):
        """User|Profile signup."""
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserModelSerializer(user).data
        return Response(data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def patients(self, request):
        """Retrieve all doctor's patients."""
        serializer_class = self.get_serializer_class()
        doctor = request.user
        queryset = Patient.objects.filter(doctor=doctor)
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)