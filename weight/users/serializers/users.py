"""Users Serializers."""

# Django
from django.contrib.auth import password_validation, authenticate

# Django Rest Framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token

# Model
from weight.users.models import (
    User,
    Profile,
    Speciality,
    RegistrationType)

# Serializers
from weight.users.serializers.profiles import ProfileModelSerializer


class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    profile = ProfileModelSerializer(read_only=True)

    class Meta:
        """Meta serializer."""

        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'profile'
        )


class UserLoginSerializer(serializers.Serializer):
    """Users login Serializer.

    Handle login request data.
    """

    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)

    def validate(self, data):
        """Check credentials."""
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credential')
        self.context['user'] = user
        return data

    def create(self, data):
        """Generate or retrieve new token."""
        # Token is one to one field with user
        token, created = Token.objects.get_or_create(user=self.context.get('user'))
        return self.context['user'], token.key


class UserSignUpSerializer(serializers.Serializer):
    """Users signup serializer.

    Handle sign up data validation and user/profile creation.
    """

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.SlugField(
        max_length=14,
        min_length=4,
        # unique field respect circles objecs
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    # Password
    password = serializers.CharField(max_length=14, min_length=4)
    password_confirmation = serializers.CharField(max_length=14, min_length=4)

    # Name
    first_name = serializers.CharField(min_length=1)
    last_name = serializers.CharField(min_length=1)

    # Profile
    speciality = serializers.SlugField(
        max_length=40
    )
    registration_type = serializers.SlugField(
        max_length=40
    )
    registration_number = serializers.CharField(min_length=1)

    def validate_speciality(self, data):
        """Validate speciality slugname."""
        try:
            speciality = Speciality.objects.get(slug_name=data)
        except Speciality.DoesNotExist:
            speciality = None
        if not speciality:
            raise serializers.ValidationError("Speciality does not exist by slugname.")
        return speciality

    def validate_registration_type(self, data):
        """Validate registration type slugname."""
        try:
            registration_type = RegistrationType.objects.get(slug_name=data)
        except RegistrationType.DoesNotExist:
            registration_type = None
        if not registration_type:
            raise serializers.ValidationError("Speciality does not exist by slugname.")
        return registration_type

    def validate(self, data):
        """Verify password match."""
        passwd = data.get('password')
        passwd_conf = data.get('password_confirmation')
        if passwd != passwd_conf:
            raise serializers.ValidationError("Passwords does not match.")
        password_validation.validate_password(passwd)
        return data

    def create(self, data):
        """Handle user and profile creation."""
        data.pop('password_confirmation')
        # Profile data
        profile_data = {}
        for field in Profile._meta.local_fields:
            if field.name in data:
                profile_data[field.name] = data.pop(field.name)

        user = User.objects.create_user(**data)
        Profile.objects.create(
            user=user,
            **profile_data
        )
        return user
    
