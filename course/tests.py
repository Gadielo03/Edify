from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Course, Module, Lesson, UserProgress, CourseReview

User = get_user_model()


class CourseModelTest(TestCase):
    """Tests para el modelo Course"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher@test.com',
            password='testpass123',
            first_name='Teacher',
            last_name='One',
            role=User.IS_TEACHER
        )
        
        self.student = User.objects.create_user(
            username='student1',
            email='student@test.com',
            password='testpass123',
            first_name='Student',
            last_name='One',
            role=User.IS_STUDENT
        )
        
        self.course = Course.objects.create(
            owner=self.teacher,
            title='Test Course',
            slug='test-course',
            description='A test course description'
        )
        
        self.module = Module.objects.create(
            course=self.course,
            title='Module 1',
            order=1
        )
        
        self.lesson1 = Lesson.objects.create(
            module=self.module,
            title='Lesson 1',
            content_type='text',
            text_content='Test content',
            order=1
        )
        
        self.lesson2 = Lesson.objects.create(
            module=self.module,
            title='Lesson 2',
            content_type='video',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            order=2
        )
    
    def test_course_creation(self):
        """Test 1: Verificar que un curso se crea correctamente"""
        self.assertEqual(self.course.title, 'Test Course')
        self.assertEqual(self.course.slug, 'test-course')
        self.assertEqual(self.course.owner, self.teacher)
        self.assertEqual(str(self.course), 'Test Course')
    
    def test_module_creation(self):
        """Test 2: Verificar que un módulo se crea correctamente"""
        self.assertEqual(self.module.title, 'Module 1')
        self.assertEqual(self.module.course, self.course)
        self.assertEqual(self.module.order, 1)
    
    def test_lesson_creation(self):
        """Test 3: Verificar que una lección se crea correctamente"""
        self.assertEqual(self.lesson1.title, 'Lesson 1')
        self.assertEqual(self.lesson1.content_type, 'text')
        self.assertEqual(self.lesson1.module, self.module)
    
    def test_course_progress_calculation_no_progress(self):
        """Test 4: Verificar cálculo de progreso sin lecciones completadas"""
        progress = self.course.get_progress(self.student)
        self.assertEqual(progress, 0)
    
    def test_course_progress_calculation_partial(self):
        """Test 5: Verificar cálculo de progreso parcial"""
        UserProgress.objects.create(
            user=self.student,
            lesson=self.lesson1,
            is_completed=True
        )
        progress = self.course.get_progress(self.student)
        self.assertEqual(progress, 50.0)
    
    def test_course_progress_calculation_complete(self):
        """Test 6: Verificar cálculo de progreso completo"""
        UserProgress.objects.create(
            user=self.student,
            lesson=self.lesson1,
            is_completed=True
        )
        UserProgress.objects.create(
            user=self.student,
            lesson=self.lesson2,
            is_completed=True
        )
        progress = self.course.get_progress(self.student)
        self.assertEqual(progress, 100.0)
    
    def test_youtube_url_extraction(self):
        """Test 7: Verificar extracción de URL de YouTube"""
        embed_url = self.lesson2.get_youtube_embed_url()
        self.assertIsNotNone(embed_url)
        self.assertIn('youtube-nocookie.com/embed/dQw4w9WgXcQ', embed_url)


class CourseListViewTest(TestCase):
    """Tests para la vista de lista de cursos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='testpass123',
            role=User.IS_TEACHER
        )
        
        self.course1 = Course.objects.create(
            owner=self.teacher,
            title='Course 1',
            slug='course-1',
            description='Description 1'
        )
        
        self.course2 = Course.objects.create(
            owner=self.teacher,
            title='Course 2',
            slug='course-2',
            description='Description 2'
        )
        
        self.list_url = reverse('course:list')
    
    def test_course_list_view_get(self):
        """Test 8: Verificar que la página de lista de cursos carga correctamente"""
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course/course_list.html')
        self.assertEqual(len(response.context['courses']), 2)
    
    def test_course_list_view_displays_courses(self):
        """Test 9: Verificar que la lista muestra todos los cursos"""
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(self.list_url)
        self.assertContains(response, 'Course 1')
        self.assertContains(response, 'Course 2')


class CourseCreateViewTest(TestCase):
    """Tests para la vista de creación de cursos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='testpass123',
            role=User.IS_TEACHER
        )
        
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123',
            role=User.IS_STUDENT
        )
        
        self.create_url = reverse('course:create')
    
    def test_course_create_requires_login(self):
        """Test 10: Verificar que crear curso requiere autenticación"""
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)
    
    def test_course_create_requires_teacher_role(self):
        """Test 11: Verificar que solo maestros pueden crear cursos"""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
    
    def test_course_create_view_accessible_by_teacher(self):
        """Test 12: Verificar que maestros pueden acceder a crear curso"""
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course/course_create.html')


class CourseDetailViewTest(TestCase):
    """Tests para la vista de detalle de curso"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='testpass123',
            role=User.IS_TEACHER
        )
        
        self.course = Course.objects.create(
            owner=self.teacher,
            title='Test Course',
            slug='test-course',
            description='Test description'
        )
        
        self.module = Module.objects.create(
            course=self.course,
            title='Module 1',
            order=1
        )
        
        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Lesson 1',
            content_type='text',
            text_content='Content',
            order=1
        )
        
        self.detail_url = reverse('course:detail', kwargs={'slug': self.course.slug})
    
    def test_course_detail_view_get(self):
        """Test 13: Verificar que la página de detalle de curso carga correctamente"""
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course/course_detail.html')
        self.assertEqual(response.context['course'].title, 'Test Course')
    
    def test_course_detail_shows_modules_and_lessons(self):
        """Test 14: Verificar que el detalle muestra módulos y lecciones"""
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(self.detail_url)
        self.assertContains(response, 'Module 1')
        self.assertContains(response, 'Lesson 1')


class UserProgressTest(TestCase):
    """Tests para el progreso del usuario"""
    
    def setUp(self):
        """Configuración inicial"""
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123',
            role=User.IS_STUDENT
        )
        
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='testpass123',
            role=User.IS_TEACHER
        )
        
        self.course = Course.objects.create(
            owner=self.teacher,
            title='Test Course',
            slug='test-course',
            description='Description'
        )
        
        self.module = Module.objects.create(
            course=self.course,
            title='Module 1',
            order=1
        )
        
        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Lesson 1',
            content_type='text',
            text_content='Content',
            order=1
        )
    
    def test_user_progress_creation(self):
        """Test 15: Verificar que el progreso del usuario se crea correctamente"""
        progress = UserProgress.objects.create(
            user=self.student,
            lesson=self.lesson,
            is_completed=True
        )
        self.assertEqual(progress.user, self.student)
        self.assertEqual(progress.lesson, self.lesson)
        self.assertTrue(progress.is_completed)


class CourseReviewTest(TestCase):
    """Tests para las reseñas de cursos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123',
            role=User.IS_STUDENT
        )
        
        self.teacher = User.objects.create_user(
            username='teacher',
            email='teacher@test.com',
            password='testpass123',
            role=User.IS_TEACHER
        )
        
        self.course = Course.objects.create(
            owner=self.teacher,
            title='Test Course',
            slug='test-course',
            description='Description'
        )
    
    def test_course_review_creation(self):
        """Test 16: Verificar que una reseña se crea correctamente"""
        review = CourseReview.objects.create(
            course=self.course,
            user=self.student,
            rating=5,
            comment='Excellent course!'
        )
        self.assertEqual(review.course, self.course)
        self.assertEqual(review.user, self.student)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excellent course!')
    
    def test_course_review_str_representation(self):
        """Test 17: Verificar la representación en string de una reseña"""
        review = CourseReview.objects.create(
            course=self.course,
            user=self.student,
            rating=4,
            comment='Good course'
        )
        expected_str = f"student - Test Course (4/5)"
        self.assertEqual(str(review), expected_str)

