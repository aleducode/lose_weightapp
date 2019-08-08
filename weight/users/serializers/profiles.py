"""Profiles Serializers."""

# Django Rest Framework
from rest_framework import serializers

# Model
from weight.users.models import Profile


class ProfileModelSerializer(serializers.ModelSerializer):
    """Profile model serializer."""

    speciality = serializers.StringRelatedField()
    registration_type = serializers.StringRelatedField()

    class Meta:
        """Meta class."""

        model = Profile
        fields = (
            'registration_number',
            'speciality',
            'registration_type'
        )
        read_only_fields = (
            'registration_number',
        )
