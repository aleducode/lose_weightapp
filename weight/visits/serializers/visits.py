"""Visit Serializers."""

# Django Rest Framework
from rest_framework import serializers


# Model
from weight.visits.models import Visit

# Serializer
from weight.patients.serializers import PatientModelSerializer
from weight.users.serializers import UserModelSerializer


class VisitModelSerializer(serializers.ModelSerializer):
    """Visit model serializer."""

    class Meta:
        """Meta serializer."""

        model = Visit
        fields = (
            'weight',
            'height',
            'type_visit',
            'risk_factor'
        )


class CreateVisitModelModelSerializer(serializers.ModelSerializer):
    """Create patient's visit."""

    doctor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    risk_factor = serializers.BooleanField(required=True)

    class Meta:
        """Meta class."""

        model = Visit
        exclude = ('created', 'modified', 'id', 'patient')

    def validate_type_visit(self, data):
        """Validate unique first visit."""
        if data == 'First':
            if 'height' not in self.initial_data:
                raise serializers.ValidationError('height field is required')
            first_visit_already_exists = Visit.objects.filter(
                patient=self.context['patient'].pk,
                type_visit='First'
            )
            if first_visit_already_exists:
                raise serializers.ValidationError('First visit already exist for this user.')
        return data

    def imc_calcle(self, weight, height):
        """Calcle imc."""
        # convert weight to mts.
        height = height/100
        return weight/(height**2)

    def create(self, data):
        """Create Visit for patient and build result data."""
        result = 'next-form'
        patient = self.context['patient']
        if data['type_visit'] == 'First':
            imc = self.imc_calcle(self.context['height'], self.context['weight'])
            
            if imc < 27:
                result = 'Naltrasena bupropin no esta indicado para imc'
            elif imc > 27 and imc < 29.9 and not data['risk_factor']:
                result = 'Naltrasena bupropin no esta indicado para imc en ausencia'

            if patient.age() < 18:
                result = 'Naltrasena bupropin no ha sido testeada en menores de 18.'
        else:
            pass
        data['patient'] = patient
        visit = Visit.objects.create(**data)
        return [visit, result]
