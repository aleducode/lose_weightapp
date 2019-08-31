"""Visits urls."""

# Django
from django.urls import include, path

# Django Rest Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import visits as visit_views

router = DefaultRouter()
router.register(
    r'patients/(?P<username>[a-zA-Z0-9_-]+)/visits',
    visit_views.PatientViewSet,
    basename='visit'
)
urlpatterns = [
    path('', include(router.urls))
]
