"""User forms."""

# Django
from django import forms


class ChangePasswordForm(forms.Form):
    """Sign up form."""

    def __init__(self, *args, **kwargs):
        """Override init function to get user in session."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    password = forms.CharField(
        min_length=7,
        max_length=20,
        label='Nueva Contraseña',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
            }
        )
    )

    password_confirmation = forms.CharField(
        min_length=7,
        max_length=20,
        label='Confirmar nueva Contraseña',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
            }
        )
    )

    def clean(self):
        """Verify password confirmation match."""
        data = super().clean()
        password = data['password']
        password_confirmation = data['password_confirmation']
        if password != password_confirmation:
            raise forms.ValidationError('Password do not match')
        return data
    
    def save(self):
        """Update user password."""
        data = self.cleaned_data
        data.pop('password_confirmation')
        user = self.user
        user.set_password(data['password'])
        user.save()
