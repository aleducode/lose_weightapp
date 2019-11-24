"""Users views."""

# Django
from django.views.generic import (
    FormView
)
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, Http404


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

# Forms
from weight.users.forms import ChangePasswordForm

# Serializers
from weight.users.serializers import (
    UserModelSerializer,
    UserLoginSerializer,
    UserSignUpSerializer,
    ChangePasswordSerializer
    )
from weight.patients.serializers import PatientModelSerializer

# Models
from weight.users.models import User
from weight.patients.models import Patient

# Utils
import jwt



class UserViewSet(mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """User view set.

    Handle login and signup.
    """

    queryset = User.objects.all()
    lookup_field = 'username'

    def get_permissions(self):
        """Assign permission based on action."""
        if self.action in ['signup', 'login', 'change_password']:
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
        if self.action == 'change_password':
            return ChangePasswordSerializer
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
        user, token = serializer.save()
        data = {
            'user': UserModelSerializer(user).data,
            'access_token': token
        }
        return Response(data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def patients(self, request):
        """Retrieve all doctor's patients."""
        serializer_class = self.get_serializer_class()
        doctor = request.user
        queryset = Patient.objects.filter(doctor=doctor)
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change password email."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'response': 'Email sent.'
        }
        return Response(data, status=status.HTTP_200_OK)


class ChangePasswordView(FormView):
    """Change password."""
    
    template_name = 'reset-password.html'
    form_class = ChangePasswordForm

    def dispatch(self, request, *args, **kwargs):
        """Validate token."""
        token = request.GET.get('token', None)
        self.error = None
        self.user = None
        payload = None
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                self.error = 'Verification link has expired.'
            except jwt.PyJWTError:
                self.error = 'Invalid token'
            if payload:
                if payload.get('type') != 'reset-password':
                    self.error = 'Invalid token'
                if not self.error:
                    username = payload.get('user', None)
                    self.user = User.objects.get(username=username)
        else:
            raise Http404 
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Set user in form context."""
        kwargs = super().get_form_kwargs()
        if self.user:
            kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        """Pass possible error to template."""
        context = super().get_context_data(**kwargs)
        if self.error:
            messages.error(self.request, self.error)
        return context
    
    def form_valid(self, form):
        """Validate form."""
        form.save()
        messages.success(self.request, 'Contraseña acutalizada.')
        return render(self.request, self.template_name)