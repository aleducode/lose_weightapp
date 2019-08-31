"""Visit Serializers."""

# Django Rest Framework
from rest_framework import serializers
from django.utils import timezone

# Model
from weight.visits.models import Visit
from weight.patients.serializers import PatientModelSerializer


class VisitModelSerializer(serializers.ModelSerializer):
    """Visit model serializer."""

    patient = PatientModelSerializer(read_only=True)

    class Meta:
        """Meta serializer."""

        model = Visit
        fields = (
            'patient',
            'weight',
            'height',
            'type_visit',
            'risk_factor',
            'created'
        )


class CreateVisitModelModelSerializer(serializers.ModelSerializer):
    """Create patient's visit."""

    doctor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    risk_factor = serializers.BooleanField(required=True)
    height = serializers.FloatField(min_value=140, max_value=210, required=False)
    weight = serializers.FloatField(min_value=50, max_value=180)

    class Meta:
        """Meta class."""

        model = Visit
        exclude = ('created', 'modified', 'id', 'patient')

    def validate_type_visit(self, data):
        """Validate unique first visit."""
        if data == 'First':
            first_visit_already_exists = Visit.objects.filter(
                patient=self.context['patient'].pk,
                type_visit='First'
            )
            if first_visit_already_exists:
                raise serializers.ValidationError('First visit already exist for this user.')
        return data

    def validate(self, data):
        """Valiate height range."""
        if data['type_visit'] == 'First':
            if 'height' not in data:
                raise serializers.ValidationError('height field is required')
        return data

    def imc_calcle(self, weight, height):
        """Calcle imc."""
        # convert weight to mts.
        height = float(height)/100
        return float(weight)/(height**2)

    def create(self, data):
        """Create Visit for patient and build result data."""
        result = 'next-form'
        patient = self.context['patient']
        if data['type_visit'] == 'First':
            imc = self.imc_calcle(self.data['height'], self.data['weight'])

            if imc < 27:
                result = 'NALTREXONA - BUPROPION no está indicado si el IMC es menor a 27.'
            elif imc > 27 and imc < 29.9 and not data['risk_factor']:
                result = 'NALTREXONA - BUPROPION no está indicado si el IMC está entre 27 y 29.9 en ausencia de\
                          factores de riesgo cardiovascular (hipertensión arterial, diabetes o dislipidemia).'

            if patient.age() < 18:
                result = 'NALTREXONA - BUPROPION no ha sido testeado en menores de 18 años.'
        else:
            firt_visit = Visit.objects.get(
                patient=patient.pk,
                type_visit='First'
            )
            follow_up_visits = Visit.objects.filter(
                patient=patient.pk,
                type_visit='Follow-Up'
            )
            treatment_weaks = (timezone.now() - firt_visit.created).days/7
            if treatment_weaks >= 12:
                if follow_up_visits:
                    weights_evolution = []
                    for visit in follow_up_visits:
                        weights_evolution.append(visit.weight)
                    min_weight = min(weights_evolution)
                else:
                    min_weight = firt_visit.weight
                percentage_evolution = ((data['weight'] - min_weight)/min_weight)*100
                if not percentage_evolution < 5:
                    result = 'El paciente no hay reducido al menos el 5% de su peso inicial\
                              en 12 o más semanas de tratamiento y debe suspender el tratamiento\
                              de NALTREXONA - BUPROPION.'

        data['patient'] = patient
        visit = Visit.objects.create(**data)
        return [visit, result]
