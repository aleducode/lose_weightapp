"""Visit Serializers."""

# Django Rest Framework
from rest_framework import serializers
from django.utils import timezone

# Model
from weight.visits.models import (
    Visit,
    FirstVisitComplementInformation,
    FollowUpVisitComplementInformation,
    INSUFICIENCIA_CHOICES)
from weight.utils.models import FUNCION_RENAL_CHOICES
# Serializer
from weight.patients.serializers import PatientModelSerializer

# Utils
from utils.text import (
    first_visit_contra_indicado,
    follow_visit_suspender,
    follow_visit_evaluar
)


class VisitModelSerializer(serializers.ModelSerializer):
    """Visit model serializer."""

    patient = PatientModelSerializer(read_only=True)

    class Meta:
        """Meta serializer."""

        model = Visit
        fields = (
            'patient', 'weight',
            'height', 'type_visit',
            'risk_factor', 'created',
            'result', 'concept',
            'id', 'result_header',
            'percentage_evolution',
            'treatment_weaks'
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
        if data == 'first':
            first_visit_already_exists = Visit.objects.filter(
                patient=patient,
                type_visit='first'
            )
            if first_visit_already_exists:
                raise serializers.ValidationError('first visit already exist for this user.')
        else:
            first_visit = Visit.objects.filter(
                patient=patient,
                type_visit='first'
            )
            if not first_visit:
                raise serializers.ValidationError('To create follow-Up visit, needs first visit creation.')
            elif first_visit.get().concept in ['NO INDICADO', 'SUSPENDER']:
                raise serializers.ValidationError('User concept is NO INDICADO or SUSPENDER.')
        return data

    def validate(self, data):
        """Valiate height range."""
        if data['type_visit'] == 'first':
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
        if data['type_visit'] == 'first':
            imc = self.imc_calcle(self.data['weight'], self.data['height'])
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
                type_visit='first'
            )
            treatment_weaks = int((timezone.now() - first_visit.created).days/7)
            # TODO: review valude (+/-)
            percentage_evolution = round((
                ((data['weight'] - first_visit.weight)/first_visit.weight)*100), 1)
            # Store variables
            data['percentage_evolution'] = percentage_evolution
            data['treatment_weaks'] = treatment_weaks

            if treatment_weaks >= 12:

                if percentage_evolution > -5:
                    concept = 'SUSPENDER'
                    result = """El paciente no hay reducido al menos el 5% de su peso inicial
                              en 12 o más semanas de tratamiento y debe suspender el tratamiento
                              de NALTREXONA - BUPROPION."""

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
            type_visit='first'
        )
        if not first_visit:
            raise serializers.ValidationError('first visit is required to create complement info.')
        elif first_visit.get().concept in ['NO INDICADO', 'SUSPENDER']:
            raise serializers.ValidationError('User concept is NO INDICADO or SUSPENDER.')
        first_complement_visit = FirstVisitComplementInformation.objects.filter(
            visit=first_visit.get().pk
        )
        if first_complement_visit:
            raise serializers.ValidationError('first complement visit already exist.')

        return data

    def create(self, data):
        """Analyize user data to emit a concept and result."""
        patient = self.context['patient']
        concept = None
        result = result_header = reason_contra_indicado = ''
        keys_contra_indicado = ['depresion_mayor', 'otros_transtornos', 'hta_no_controlada',
                                'convulsiones', 'anorexia', 'abuso_alcohol', 'tratamiento_actual',
                                'alergia_naltrexona', 'embarazo', 'insuficiencia_hepatica',
                                'glaucoma', 'funcion_renal', 'intolerancia_lactosa']

        for value in keys_contra_indicado:
            if value not in ['insuficiencia_hepatica', 'funcion_renal'] and data[value]:
                reason_contra_indicado += first_visit_contra_indicado[value]
            elif value == 'insuficiencia_hepatica':
                if data[value] == 'moderada':
                    reason_contra_indicado += (
                        '{}: {}\n'.format(
                            first_visit_contra_indicado[value],
                            INSUFICIENCIA_CHOICES[2][1])
                    )
            elif value == 'funcion_renal':
                if data[value] == 'irc-terminal':
                    reason_contra_indicado += (
                        '{}:{}\n'.format(first_visit_contra_indicado[value], FUNCION_RENAL_CHOICES[4][1])
                    )
        if reason_contra_indicado:
            concept = 'CONTRA INDICADO'
            result = reason_contra_indicado
            result_header = """El paciente tiene las siguientes
                            contraindicaciones para recibir NALTREXONA
                            - BUPROPION."""
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
            if data['funcion_renal'] in ['moderada', 'severa']:
                result += 'PRECAUCIÓN. LA MÁXIMA DOSIS RECOMENDADA EN EL SEGUIMIENTO ES 1 COMPRIMIDO A LA MAÑANA Y 1 COMPRIMIDO A LA NOCHE.\n'
            if data['palpitaciones_aumento_fc']:
                result += 'NALTREXONA - BUPROPION PUEDE AUMENTAR LA FRECUENCIA CARDIACA Y LA PRESIÓN ARTERIAL POR LO QUE SE RECOMIENDA UN CONTROL ESTRICTO DE LA FC Y LA TA.\n'
            if data['tratamiento_levodopa']:
                result += 'PRECAUCIÓN. EL USO DE NALTREXONA - BUPROPION JUNTO CON ESTOS MEDICAMENTOS INCREMENTA EL RIESGO DE EVENTOS ADVERSOS.\n'
            concept = 'INDICADO'
            # TODO: fix format
            result_header = """Su paciente podría recibir NALTREXONA - BUPROPION como
                            complemento de una dieta reducida en calorías y de actividad
                            física para el control crónico del peso.
                            Iniciar tratamiento con 1 comprimido (8mg/90mg) por la
                            mañana (NO junto a comidas grasas). Los comprimidos no
                            deben ser cortados, masticados ni triturados.\n
                            Si se omitió una dosis, ésta debe saltearse y reanudar la
                            administración al momento de la siguiente dosis."""
        # Get visit
        first_visit = Visit.objects.get(
            patient=patient,
            type_visit='first')
        data['visit'] = first_visit

        # Create complement visit information
        FirstVisitComplementInformation.objects.create(**data)
        first_visit.result = result
        first_visit.result_header = result_header
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
            type_visit='first'
        )
        if not first_visit:
            raise serializers.ValidationError(
                'first visit is required to create complement info.'
            )
        elif first_visit.get().concept in ['NO INDICADO', 'SUSPENDER']:
            raise serializers.ValidationError('User concept is NO INDICADO.')

        follow_up = Visit.objects.filter(
            patient=patient,
            type_visit='follow-up'
        )
        if not follow_up:
            raise serializers.ValidationError('Follow Up visit is required to create complement data.')

        return data

    def create(self, data):
        """Analyize user data to emit a concept and result."""
        concept = None
        result = ''
        result_header = reason_suspender  = ''
        keys_visit_suspender = ['depresion_mayor', 'otros_transtornos', 'hta_no_controlada',
                                'convulsiones', 'anorexia', 'abuso_alcohol',
                                'tratamiento_actual', 'embarazo',
                                'hepatitis_aguda', 'glaucoma', 'disfuncion_renal',
                                'intolerancia_lactosa', 'suspendio']

        keys_visit_evaluar = ['nauseas', 'constipacion', 'cefalea',
                              'mareos', 'insomnio', 'boca_seca',
                              'diarrea', 'vomitos', 'dolor_abdominal',
                              'otros_eventos']

        for value in keys_visit_suspender:
            if value != 'disfuncion_renal' and data[value]:
                reason_suspender += follow_visit_suspender[value]
            elif value == 'disfuncion_renal':
                if data[value] == 'irc-terminal':
                    reason_suspender += (
                        '{}:{}\n'.format(
                            follow_visit_suspender[value], FUNCION_RENAL_CHOICES[4][1])
                    )
        for value in keys_visit_evaluar:
                if data[value]:
                    reason_suspender += 'Evaluar continuidad debido a: {}'.format(
                        follow_visit_evaluar[value])
        if reason_suspender:
            concept = 'SUSPENDER'
            result = reason_suspender
            result_header = """El paciente tiene las siguientes
                            contraindicaciones y debe suspender el
                            tratamiento de NALTREXONA - BUPROPION."""
        else:
            if data['factores_predisponentes']:
                result += 'PRECAUCIÓN.PARA REDUCIR EL RIESGO DE CONVULSIONES SE RECOMIENDA UNA DOSIS TOTAL DE MAXIMO 4 COMPRIMIDOS POR DÍA. DIVIDIR LA DOSIS DIARIA EN DOS TOMAS, ESCALAR LA DOSIS DE MANERA GRADUAL.\n'
            if data['tratamiento_beta_bloqueantes']:
                result += ' LA MÁXIMA DOSIS RECOMENDADA ES 1 COMPRIMIDO A LA MAÑANA Y 1 COMPRIMIDO A LA NOCHE.\n'
            if data['disfuncion_renal'] in ['moderada', 'severa']:
                result += 'PRECAUCIÓN. LA MÁXIMA DOSIS RECOMENDADA EN EL SEGUIMIENTO ES 1 COMPRIMIDO A LA MAÑANA Y 1 COMPRIMIDO A LA NOCHE.\n'
            if result != '':
                concept = 'AJUSTAR DOSIS'
                result_header = """Su paciente podría continuar recibiendo NALTREXONA - BUPROPION como
                                complemento de una dieta reducida en calorías y de actividad física para el
                                control crónico del peso."""
        if not concept:
            if data['tratamiento_hipoglucemiantes']:
                result += 'DEBE TENERSE PRECAUCIÓN CON EL RIESGO DE HIPOGLUCEMIA Y CONSIDERAR DISMINUIR DOSIS DE HIPOGLUCEMIANTES. SE RECOMIENDA MEDICIÓN PERIÓDICA DE GLUCEMIA.\n'
            if data['actividad_fisica'] in ['no', 'uno-dos']:
                result += 'ES RECOMENDABLE INICIAR ACTIVIDAD FÍSICA O INCREMENTAR LA FRECUENCIA A 3 VECES POR SEMANA.\n'
            if not data['dieta_hipocalorica']:
                result += 'RECOMENDAR DIETA HIPOCALÓRICA.\n'
            if data['palpitaciones_aumento_fc']:
                result += 'NALTREXONA - BUPROPION PUEDE AUMENTAR LA FRECUENCIA CARDIACA Y LA PRESIÓN ARTERIAL POR LO QUE SE RECOMIENDA UN CONTROL ESTRICTO DE LA FC Y LA TA.\n'
            if data['hipertension_arterial']:
                result += ' NALTREXONA - BUPROPION PUEDE AUMENTAR LA PRESIÓN ARTERIAL POR LO QUE SE RECOMIENDA UN CONTROL ESTRICTO LA TA.\n'
            if data['tratamiento_levodopa']:
                result += 'EL USO DE NALTREXONA - BUPROPION JUNTO CON ESTOS MEDICAMENTOS INCREMENTA EL RIESGO DE EVENTOS ADVERSOS.\n'
            if result != '':
                concept = 'ALERTA'
                result_header = """Su paciente podría continuar recibiendo NALTREXONA - BUPROPION como
                                complemento de una dieta reducida en calorías y de actividad física para el
                                control crónico del peso."""
        if concept not in ['ALERTA', 'SUSPENDER', 'AJUSTAR DOSIS']:
            concept = 'CONTINUAR'
            result_header = """Su paciente podría continuar recibiendo NALTREXONA -
                                BUPROPION como complemento de una dieta reducida en
                                calorías y de actividad física para el control crónico del peso.\n"""

        # Update result visit and create follow information complement
        # TODO: collect and send by context
        first_visit = Visit.objects.get(
            patient=self.context['patient'],
            type_visit='first'
        )
        visit = Visit.objects.get(pk=data['visit'])
        data['visit'] = visit
        FollowUpVisitComplementInformation.objects.create(**data)

        if concept == 'CONTINUAR':
            treatment_weaks = int((timezone.now() - first_visit.created).days/7)
            if treatment_weaks == 2:
                result_header = """
                                Iniciar tratamiento con 1 comprimido (8mg/90mg) por la
                                mañana y 1 comprimido (8mg/90mg) por la noche (NO junto
                                a comidas grasas). Los comprimidos no deben ser cortados,
                                masticados ni triturados.\n
                                Si se omitió una dosis, ésta debe saltearse y reanudar la
                                administración al momento de la siguiente dosis."""
            elif treatment_weaks == 3:
                result_header = """
                                Iniciar tratamiento con 2 comprimido (8mg/90mg) por la
                                mañana y 1 comprimido (8mg/90mg) por la noche (NO junto
                                a comidas grasas). Los comprimidos no deben ser cortados,
                                masticados ni triturados.\n
                                Si se omitió una dosis, ésta debe saltearse y reanudar la
                                administración al momento de la siguiente dosis."""
            elif treatment_weaks > 4:
                result_header = """
                                Iniciar tratamiento con 2 comprimido (8mg/90mg) por la
                                mañana y 2 comprimido (8mg/90mg) por la noche (NO junto
                                a comidas grasas). Los comprimidos no deben ser cortados,
                                masticados ni triturados.
                                Si se omitió una dosis, ésta debe saltearse y reanudar la
                                administración al momento de la siguiente dosis."""

        visit.result = result
        visit.concept = concept
        visit.result_header = result_header
        visit.save()
        # Refresh info to return
        follow_visit = Visit.objects.get(pk=visit.pk)

        return follow_visit
