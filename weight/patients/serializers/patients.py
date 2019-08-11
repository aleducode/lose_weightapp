"""Patients Serializers."""

# Django
from django.contrib.auth import password_validation, authenticate

# Django Rest Framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token

# Model
from weight.patients.models import Patient

INPUT_FORMATS = ['%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d']


class PatientModelSerializer(serializers.ModelSerializer):
    """Patient model serializer."""

    class Meta:
        """Meta serializer."""

        model = Patient
        fields = (
            'name',
            'document',
            'gender',
            'birthdate'
        )


class CreatePatientModelSerializer(serializers.ModelSerializer):
    """Create patient Serializer."""

    doctor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    birthdate = serializers.DateField(format='%Y-%m-%d', input_formats=INPUT_FORMATS)
    document = serializers.SlugField(
        validators=[UniqueValidator(queryset=Patient.objects.all())],
        max_length=10

    )

    class Meta:
        """Meta class."""

        model = Patient
        exclude = ('created', 'modified', 'id')