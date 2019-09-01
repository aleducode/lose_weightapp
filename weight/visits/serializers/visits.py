"""Visit Serializers."""

# Django Rest Framework
from rest_framework import serializers
from django.utils import timezone

# Model
from weight.visits.models import (
    Visit,
    FirstVisitComplementInformation,
    FollowUpVisitComplementInformation)

# Serializer
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
            'created',
            'result',
            'concept',
            'id'
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
        patient = self.context['patient'].pk
        if data == 'First':
            first_visit_already_exists = Visit.objects.filter(
                patient=patient,
                type_visit='First'
            )
            if first_visit_already_exists:
                raise serializers.ValidationError('First visit already exist for this user.')
        else:
            first_visit = Visit.objects.filter(
                patient=patient,
                type_visit='First'
            )
            if not first_visit:
                raise serializers.ValidationError('To create follow-Up visit, needs first visit creation.')
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
        result = ''
        concept = ''
        patient = self.context['patient']
        if data['type_visit'] == 'First':
            imc = self.imc_calcle(self.data['height'], self.data['weight'])

            if imc < 27:
                result = 'NALTREXONA - BUPROPION no está indicado si el IMC es menor a 27.'
                concept = 'NO INDICADO'
            elif imc > 27 and imc < 29.9 and not data['risk_factor']:
                concept = 'NO INDICADO'
                result = 'NALTREXONA - BUPROPION no está indicado si el IMC está entre 27 y 29.9 en ausencia de\
                          factores de riesgo cardiovascular (hipertensión arterial, diabetes o dislipidemia).'

            if patient.age() < 18:
                concept = 'NO INDICADO'
                result = 'NALTREXONA - BUPROPION no ha sido testeado en menores de 18 años.'
        else:
            first_visit = Visit.objects.get(
                patient=patient.pk,
                type_visit='First'
            )
            treatment_weaks = (timezone.now() - first_visit.created).days/7
            if treatment_weaks >= 12:
                percentage_evolution = abs(((data['weight'] - first_visit.weight)/first_visit.weight)*100)
                if percentage_evolution < 5:
                    concept = 'SUSPENDER'
                    result = 'El paciente no hay reducido al menos el 5% de su peso inicial\
                              en 12 o más semanas de tratamiento y debe suspender el tratamiento\
                              de NALTREXONA - BUPROPION.'

        data['patient'] = patient
        data['result'] = result
        data['concept'] = concept
        visit = Visit.objects.create(**data)
        return visit


class FirstVisitComplementSerializer(serializers.ModelSerializer):
    """FirstVisit model serializer."""

    class Meta:
        """Meta serializer."""

        model = FirstVisitComplementInformation
        exclude = ('id', 'modified', 'visit')

    def validate(self, data):
        """Check if first visit is already taken by patient."""
        patient = self.context['patient']
        first_visit = Visit.objects.filter(
            patient=patient,
            type_visit='First'
        )
        if not first_visit:
            raise serializers.ValidationError('First visit is required to create complement info.')
        elif first_visit.get().concept in ['NO INDICADO', 'SUSPENDER']:
            raise serializers.ValidationError('User concept is NO INDICADO.')
        first_complement_visit = FirstVisitComplementInformation.objects.filter(
            visit=first_visit.get().pk
        )
        if first_complement_visit:
            raise serializers.ValidationError('First complement visit already exist.')

        return data

    def create(self, data):
        """Analyize user data to emit a concept and result."""
        patient = self.context['patient']
        concept = None
        result = ''
        if data['depresion_mayor'] or data['otros_transtornos'] or data['hta_no_controlada'] or data['convulsiones'] or data['anorexia'] or data['tratamiento_actual'] or data['alergia_naltrexona'] or data['embarazo'] or data['insuficiencia_hepatica'] == 'Moderada' or data['glaucoma'] or data['funcion_renal'] == 'IRC Terminal' or data['intolerancia_lactosa']:
            concept = 'CONTRA INDICADO'
        else:
            if patient.age() > 65:
                result += 'USAR CON PRECAUCIÓN EN MAYORES DE 65 AÑOS POR MAYOR RIESGO DE EVENTOS ADVERSOS DEBIDO A LA ELIMINACIÓN RENAL DE NALTREXONA - BUPROPION.\n'
            if data['tratamiento_hipoglucemiantes']:
                result += 'SE RECOMIENDA MEDIR RUTINARIAMENTE LA GLUCEMIA. DEBE TENERSE PRECAUCIÓN CON EL RIESGO DE HIPOGLUCEMIA Y CONSIDERAR DISMINUIR LA DOSIS DE HIPOGLUCEMIANTES.\n'
            if data['factores_predisponentes']:
                result += 'PRECAUCIÓN. PARA REDUCIR EL RIESGO DE CONVULSIONES SE RECOMIENDA UNA DOSIS TOTAL DE MÁXIMO 4 COMPRIMIDOS POR DÍA. DIVIDIR LA DOSIS DIARIA EN DOS TOMAS, ESCALAR LA DOSIS DE MANERA GRADUAL.\n'
            if data['insuficiencia_hepatica'] == 'Leve':
                result += 'LA DOSIS MÁXIMA DIARIA RECOMENDADA A LOS LARGO DE TODO EL TRATAMIENTO ES DE UN COMPRIMIDO POR LA MAÑANA.\n'
            if data['tratamiento_beta_bloqueantes']:
                result += 'PRECAUCIÓN. LA MÁXIMA DOSIS RECOMENDADA EN EL SEGUIMIENTO ES 1 COMPRIMIDO A LA MAÑANA Y 1 COMPRIMIDO A LA NOCHE.\n'
            if data['actividad_fisica'] in ['no', 'uno-dos']:
                result += 'ES RECOMENDABLE INICIAR ACTIVIDAD FÍSICA O INCREMENTAR LA FRECUENCIA A 3 VECES POR SEMANA.\n'
            if not data['dieta_hipocalorica']:
                result += 'RECOMENDAR DIETA HIPOCALÓRICA.\n'
            if data['funcion_renal'] in ['Moderada', 'Severa']:
                result += 'PRECAUCIÓN. LA MÁXIMA DOSIS RECOMENDADA EN EL SEGUIMIENTO ES 1 COMPRIMIDO A LA MAÑANA Y 1 COMPRIMIDO A LA NOCHE.\n'
            if data['palpitaciones_aumento_fc']:
                result += 'NALTREXONA - BUPROPION PUEDE AUMENTAR LA FRECUENCIA CARDIACA Y LA PRESIÓN ARTERIAL POR LO QUE SE RECOMIENDA UN CONTROL ESTRICTO DE LA FC Y LA TA.\n'
            if data['tratamiento_levodopa']:
                result += 'PRECAUCIÓN. EL USO DE NALTREXONA - BUPROPION JUNTO CON ESTOS MEDICAMENTOS INCREMENTA EL RIESGO DE EVENTOS ADVERSOS.\n'
            concept = 'INDICADO'

        first_visit = Visit.objects.get(
            patient=patient,
            type_visit='First')
        data['visit'] = first_visit
        FirstVisitComplementInformation.objects.create(**data)
        first_visit.result = result
        first_visit.concept = concept
        first_visit.save()
        first_visit = Visit.objects.get(pk=first_visit.pk)
        return first_visit


class FollowUpVisitComplementSerializer(serializers.ModelSerializer):
    """FollowUp model serializer."""

    visit = serializers.IntegerField(required=True)

    class Meta:
        """Meta serializer."""

        model = FollowUpVisitComplementInformation
        exclude = ('id', 'modified')

    def validate_visit(self, data):
        """Validate follow up visit."""
        follow_up_visit = Visit.objects.filter(pk=data)
        if not follow_up_visit:
            raise serializers.ValidationError('Follow up visit does not exists.')
        else:
            follow_up_complement = FollowUpVisitComplementInformation.objects.filter(
                visit=follow_up_visit.get().pk
            ).exists()
            if follow_up_complement:
                raise serializers.ValidationError('Follow up complement visit already exists.')
        return data

    def validate(self, data):
        """Check if first visit is already taken by patient."""
        patient = self.context['patient']
        first_visit = Visit.objects.filter(
            patient=patient,
            type_visit='First'
        )
        if not first_visit:
            raise serializers.ValidationError(
                'First visit is required to create complement info.'
            )
        elif first_visit.get().concept in ['NO INDICADO', 'SUSPENDER']:
            raise serializers.ValidationError('User concept is NO INDICADO.')

        follow_up = Visit.objects.filter(
            patient=patient,
            type_visit='Follow-Up'
        )
        if not follow_up:
            raise serializers.ValidationError('Follow Up visit is required to create complement data.')

        return data

    def create(self, data):
        """Analyize user data to emit a concept and result."""
        concept = None
        result = ''
        if data['depresion_mayor'] or data['otros_transtornos'] or data['hta_no_controlada'] or data['convulsiones'] or data['anorexia'] or data['abuso_alcohol'] or data['tratamiento_actual'] or data['embarazo'] or data['hepatitis_aguda'] or data['glaucoma'] or data['disfuncion_renal'] == 'IRC Terminal' or data['intolerancia_lactosa'] or data['suspendio']:
            concept = 'SUSPENDER'
        elif data['nauseas'] or data['constipacion'] or data['cefalea'] or data['mareos'] or data['insomnio'] or data['boca_seca'] or data['diarrea'] or data['vomitos'] or data['dolor_abdominal'] or data['otros_eventos']:
            concept = 'EVALUAR LA CONTINUIDAD DEL TRATAMIENTO'
        else:
            if data['tratamiento_hipoglucemiantes']:
                result += 'DEBE TENERSE PRECAUCIÓN CON EL RIESGO DE HIPOGLUCEMIA Y CONSIDERAR DISMINUIR DOSIS DE HIPOGLUCEMIANTES. SE RECOMIENDA MEDICIÓN PERIÓDICA DE GLUCEMIA.\n'
            if data['factores_predisponentes']:
                result += 'PRECAUCIÓN.PARA REDUCIR EL RIESGO DE CONVULSIONES SE RECOMIENDA UNA DOSIS TOTAL DE MAXIMO 4 COMPRIMIDOS POR DÍA. DIVIDIR LA DOSIS DIARIA EN DOS TOMAS, ESCALAR LA DOSIS DE MANERA GRADUAL.\n'
            if data['tratamiento_beta_bloqueantes']:
                result += ' LA MÁXIMA DOSIS RECOMENDADA ES 1 COMPRIMIDO A LA MAÑANA Y 1 COMPRIMIDO A LA NOCHE.\n'
            if data['actividad_fisica'] in ['no', 'uno-dos']:
                result += 'ES RECOMENDABLE INICIAR ACTIVIDAD FÍSICA O INCREMENTAR LA FRECUENCIA A 3 VECES POR SEMANA.\n'
            if not data['dieta_hipocalorica']:
                result += 'RECOMENDAR DIETA HIPOCALÓRICA.\n'
            if data['disfuncion_renal'] in ['Moderada', 'Severa']:
                result += 'PRECAUCIÓN. LA MÁXIMA DOSIS RECOMENDADA EN EL SEGUIMIENTO ES 1 COMPRIMIDO A LA MAÑANA Y 1 COMPRIMIDO A LA NOCHE.\n'
            if data['palpitaciones_aumento_fc']:
                result += 'NALTREXONA - BUPROPION PUEDE AUMENTAR LA FRECUENCIA CARDIACA Y LA PRESIÓN ARTERIAL POR LO QUE SE RECOMIENDA UN CONTROL ESTRICTO DE LA FC Y LA TA.\n'
            if data['hipertension_arterial']:
                result += ' NALTREXONA - BUPROPION PUEDE AUMENTAR LA PRESIÓN ARTERIAL POR LO QUE SE RECOMIENDA UN CONTROL ESTRICTO LA TA.\n'
            if data['tratamiento_levodopa']:
                result += 'EL USO DE NALTREXONA - BUPROPION JUNTO CON ESTOS MEDICAMENTOS INCREMENTA EL RIESGO DE EVENTOS ADVERSOS.\n'
            concept = 'CONTINUAR'
        # Update result visit and create follow information complement
        follow_visit = Visit.objects.get(pk=data['visit'])
        data['visit'] = follow_visit
        FollowUpVisitComplementInformation.objects.create(**data)

        follow_visit.result = result
        follow_visit.concept = concept
        follow_visit.save()
        # Refresh info to return
        follow_visit = Visit.objects.get(pk=follow_visit.pk)

        return follow_visit
