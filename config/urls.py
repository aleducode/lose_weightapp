"""Main URLs module."""

from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    # Django Admin
    path(settings.ADMIN_URL, admin.site.urls),
    path('', include(('weight.users.urls', 'users'), namespace='users')),
    path('', include(('weight.patients.urls', 'patients'), namespace='patients')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
