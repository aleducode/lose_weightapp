"""Patients Serializers."""

# Django
from django.contrib.auth import password_validation, authenticate

# Django Rest Framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token

# Model
from weight.patients.models import Patient

# Utilities
from random import randint


INPUT_FORMATS = ['%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d']


class PatientModelSerializer(serializers.ModelSerializer):
    """Patient model serializer."""

    class Meta:
        """Meta serializer."""

        model = Patient
        fields = (
            'first_name',
            'last_name',
            'username',
            'gender',
            'birthdate'
        )


def random_with_n_digits(n):
    """Create random number of n digits."""
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


class CreatePatientModelSerializer(serializers.ModelSerializer):
    """Create patient Serializer."""

    doctor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    birthdate = serializers.DateField(format='%Y-%m-%d', input_formats=INPUT_FORMATS)

    class Meta:
        """Meta class."""

        model = Patient
        exclude = ('created', 'modified', 'id', 'username')

    def create(self, data):
        """Create custom username."""
        data['username'] = 'user_{}{}{}{}'.format(
            data['first_name'][0:2],
            data['last_name'][0:2],
            data['gender'][0].lower(),
            random_with_n_digits(1)
            )
        patient = Patient.objects.create(**data)
        return patient
