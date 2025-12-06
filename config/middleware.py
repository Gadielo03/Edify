from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.deprecation import MiddlewareMixin


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware que requiere autenticación para todas las rutas excepto las públicas.
    Redirige a login si el usuario no está autenticado.
    """
    
    PUBLIC_URLS = [
        '/users/login/',
        '/users/register/',
        '/',  
        '/admin/login/',  
        '/health/',
    ]
    
    PUBLIC_PREFIXES = [
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        """
        Verifica si el usuario está autenticado antes de procesar la request.
        """
        current_path = request.path_info
        if current_path in self.PUBLIC_URLS:
            return None
        
        for prefix in self.PUBLIC_PREFIXES:
            if current_path.startswith(prefix):
                return None
        
        if not request.user.is_authenticated:
            login_url = str(reverse_lazy('users:login'))
            return redirect(f'{login_url}?next={current_path}')
        
        return None
