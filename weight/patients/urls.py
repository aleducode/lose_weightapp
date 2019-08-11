"""Patients urls."""

# Django
from django.urls import include, path

# Django Rest Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import patients as patient_views

router = DefaultRouter()
router.register(r'patients', patient_views.PatientViewSet, basename='patients')

urlpatterns = [
    path('', include(router.urls))
]
