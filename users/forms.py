from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Formulario de registro para nuevos usuarios"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='¿Cómo te registrarás?'
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Cuéntanos un poco sobre ti (opcional)',
            'rows': 3
        }),
        label='Biografía'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'bio', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widgets para campos heredados
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """Formulario de inicio de sesión"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )


class UserProfileEditForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        }),
        label='Correo Electrónico'
    )
    first_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        }),
        label='Nombre'
    )
    last_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        }),
        label='Apellido'
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Cuéntanos un poco sobre ti...',
            'rows': 4
        }),
        label='Biografía'
    )
    
    # Campos opcionales para cambiar contraseña
    old_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        }),
        label='Contraseña Actual',
        help_text='Solo necesario si deseas cambiar tu contraseña'
    )
    new_password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        }),
        label='Nueva Contraseña',
        help_text='Deja en blanco si no quieres cambiar tu contraseña'
    )
    new_password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        label='Confirmar Nueva Contraseña'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['username'].help_text = 'Letras, dígitos y @/./+/-/_ solamente.'

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if any([old_password, new_password1, new_password2]):
            if not all([old_password, new_password1, new_password2]):
                raise forms.ValidationError(
                    'Para cambiar tu contraseña, debes completar todos los campos de contraseña.'
                )
            
            if not self.instance.check_password(old_password):
                raise forms.ValidationError('La contraseña actual es incorrecta.')
            
            if new_password1 != new_password2:
                raise forms.ValidationError('Las nuevas contraseñas no coinciden.')
            
            if len(new_password1) < 8:
                raise forms.ValidationError('La nueva contraseña debe tener al menos 8 caracteres.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        new_password = self.cleaned_data.get('new_password1')
        if new_password:
            user.set_password(new_password)
        
        if commit:
            user.save()
        return user
