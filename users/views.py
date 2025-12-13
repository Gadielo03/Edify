from django.shortcuts import redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserLoginForm, UserProfileEditForm


class RegisterView(CreateView):
    """Vista basada en clase para registro de nuevos usuarios"""
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        """Redirige si el usuario ya está autenticado"""
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Guarda el usuario y lo autentica automáticamente"""
        response = super().form_valid(form)
        user = self.object
        login(self.request, user)
        
        if user.is_teacher:
            messages.success(self.request, f'¡Bienvenido {user.first_name}! Te has registrado como Maestro.')
        else:
            messages.success(self.request, f'¡Bienvenido {user.first_name}! Te has registrado como Estudiante.')
        
        return response
    
    def form_invalid(self, form):
        """Muestra mensaje de error si el formulario es inválido"""
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    """Vista basada en clase para inicio de sesión"""
    form_class = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirige a la página solicitada o al home"""
        next_page = self.request.GET.get('next')
        if next_page:
            return next_page
        return reverse_lazy('home')
    
    def form_valid(self, form):
        """Muestra mensaje de bienvenida al iniciar sesión"""
        response = super().form_valid(form)
        user = self.request.user
        messages.success(self.request, f'¡Bienvenido de nuevo, {user.first_name}!')
        return response
    
    def form_invalid(self, form):
        """Muestra mensaje de error si las credenciales son incorrectas"""
        messages.error(self.request, 'Usuario o contraseña incorrectos.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """Vista basada en clase para cerrar sesión"""
    next_page = reverse_lazy('users:login')
    
    def dispatch(self, request, *args, **kwargs):
        """Muestra mensaje al cerrar sesión"""
        messages.info(request, 'Has cerrado sesión correctamente.')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """Vista basada en clase para ver el perfil del usuario"""
    template_name = 'users/profile.html'
    login_url = reverse_lazy('users:login')


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Vista basada en clase para editar el perfil del usuario"""
    form_class = UserProfileEditForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    login_url = reverse_lazy('users:login')
    
    def get_object(self, queryset=None):
        """Retorna el usuario actual"""
        return self.request.user
    
    def form_valid(self, form):
        """Guarda el usuario y mantiene la sesión si cambió la contraseña"""
        response = super().form_valid(form)
        
        # Si cambió la contraseña, mantener la sesión activa
        if form.cleaned_data.get('new_password1'):
            update_session_auth_hash(self.request, self.object)
            messages.success(
                self.request, 
                '¡Perfil actualizado correctamente! Tu contraseña ha sido cambiada.'
            )
        else:
            messages.success(self.request, '¡Perfil actualizado correctamente!')
        
        return response
    
    def form_invalid(self, form):
        """Muestra mensaje de error si el formulario es inválido"""
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)
