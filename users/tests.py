from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, UserLoginForm

User = get_user_model()


class UserModelTest(TestCase):
    """Tests para el modelo User"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.student = User.objects.create_user(
            username='estudiante1',
            email='estudiante@test.com',
            password='testpass123',
            first_name='Juan',
            last_name='Pérez',
            role=User.IS_STUDENT
        )
        
        self.teacher = User.objects.create_user(
            username='profesor1',
            email='profesor@test.com',
            password='testpass123',
            first_name='María',
            last_name='González',
            role=User.IS_TEACHER
        )
    
    def test_user_creation_student(self):
        """Test 1: Verificar que un estudiante se crea correctamente"""
        self.assertEqual(self.student.username, 'estudiante1')
        self.assertEqual(self.student.email, 'estudiante@test.com')
        self.assertEqual(self.student.role, User.IS_STUDENT)
        self.assertFalse(self.student.is_teacher)
    
    def test_user_creation_teacher(self):
        """Test 2: Verificar que un maestro se crea correctamente"""
        self.assertEqual(self.teacher.username, 'profesor1')
        self.assertEqual(self.teacher.email, 'profesor@test.com')
        self.assertEqual(self.teacher.role, User.IS_TEACHER)
        self.assertTrue(self.teacher.is_teacher)


class UserRegistrationTest(TestCase):
    """Tests para el registro de usuarios"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.register_url = reverse('users:register')
    
    def test_registration_view_get(self):
        """Test 3: Verificar que la página de registro carga correctamente"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIsInstance(response.context['form'], UserRegistrationForm)
    
    def test_registration_valid_data(self):
        """Test 4: Verificar registro exitoso con datos válidos"""
        data = {
            'username': 'nuevo_usuario',
            'email': 'nuevo@test.com',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'password1': 'ContraseñaSegura123!',
            'password2': 'ContraseñaSegura123!',
            'role': User.IS_STUDENT,
            'bio': 'Biografía de prueba'
        }
        response = self.client.post(self.register_url, data)
        
        # Verificar que el usuario fue creado
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.username, 'nuevo_usuario')
        self.assertEqual(user.email, 'nuevo@test.com')
        self.assertEqual(user.role, User.IS_STUDENT)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)


class UserLoginTest(TestCase):
    """Tests para el login de usuarios"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.login_url = reverse('users:login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_login_valid_credentials(self):
        """Test 5: Verificar login exitoso con credenciales válidas"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        
        # Verificar que el usuario está autenticado
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'testuser')
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
    
    def test_login_invalid_credentials(self):
        """Test 6: Verificar que el login falla con credenciales inválidas"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        
        # Verificar que el usuario NO está autenticado
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        # Verificar que se queda en la página de login
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
    
    def test_login_nonexistent_user(self):
        """Test 7: Verificar que el login falla con usuario inexistente"""
        data = {
            'username': 'usuarioinexistente',
            'password': 'cualquiercontraseña'
        }
        response = self.client.post(self.login_url, data)
        
        # Verificar que el usuario NO está autenticado
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.status_code, 200)


class UserProfileTest(TestCase):
    """Tests para el perfil de usuario"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@test.com',
            password='testpass123',
            first_name='Profile',
            last_name='User',
            bio='Biografía original'
        )
        self.profile_url = reverse('users:profile')
    
    def test_profile_view_requires_login(self):
        """Test 8: Verificar que el perfil requiere autenticación"""
        response = self.client.get(self.profile_url)
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)
    
    def test_profile_view_authenticated(self):
        """Test 9: Verificar que un usuario autenticado puede ver su perfil"""
        self.client.login(username='profileuser', password='testpass123')
        response = self.client.get(self.profile_url)
        
        # Verificar que la página carga correctamente
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertEqual(response.context['user'].username, 'profileuser')


class UserRegistrationFormTest(TestCase):
    """Tests para los formularios de usuario"""
    
    def test_registration_form_valid(self):
        """Test 10: Verificar que el formulario de registro acepta datos válidos"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'role': User.IS_STUDENT,
            'bio': 'Test bio'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

