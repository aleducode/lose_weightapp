"""User models admin."""

#Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Models
from weight.users.models import User, Profile


class CustomUserAdmin(UserAdmin):
    """User model admin."""
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff',)
    list_filter = ('is_staff', 'created')


@admin.register(Profile)
class PofileAdmin(admin.ModelAdmin):
    """Profile model admin."""
    list_display = ('user', 'specialty', 'registration_type', 'registration_number')
    search_fields = ('user__username', 'user__email', 'user___first_name', 'user__last_name')
    list_filter = ('specialty',)


admin.site.register(User, CustomUserAdmin)
