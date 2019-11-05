"""User models admin."""

# Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse

# Models
from weight.users.models import (
    User,
    Profile,
    RegistrationType,
    Speciality
    )

# Utilities
import csv
from datetime import datetime, timedelta


class CustomUserAdmin(UserAdmin):
    """User model admin."""

    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff',)
    list_filter = ('is_staff', 'created')
    actions = ['download_users']

    def download_users(self, request, queryset):
        """Return all users ."""
        users = User.objects.filter(
            pk__in=queryset.values_list('pk')
        ).order_by('-created')

        # Response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="allusers.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'id',
            'name',
            'username',
            'created',
            'email',
        ])
        for user in users:
            writer.writerow([
                user.pk,
                user.get_full_name(),
                user.username,
                user.created,
                user.email
            ])
        return response

    download_users.short_description = 'Download selected users'


@admin.register(Profile)
class PofileAdmin(admin.ModelAdmin):
    """Profile model admin."""

    list_display = ('user', 'speciality', 'registration_type', 'registration_number')
    search_fields = ('user__username', 'user__email', 'user___first_name', 'user__last_name')
    list_filter = ('speciality',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(RegistrationType)
admin.site.register(Speciality)
