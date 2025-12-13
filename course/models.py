from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from urllib.parse import urlparse, parse_qs
import re

class Course(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='courses_created', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return self.title
    
    def get_progress(self, user):
        total_lessons = Lesson.objects.filter(module__course=self).count()
        if total_lessons == 0: return 0
        completed = UserProgress.objects.filter(user=user, lesson__module__course=self, is_completed=True).count()
        return (completed / total_lessons) * 100

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    CONTENT_CHOICES = (
        ('video', 'Video'),
        ('pdf', 'Documento PDF'),
        ('text', 'Solo Texto'),
    )
    
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=10, choices=CONTENT_CHOICES)
    video_url = models.URLField(blank=True, null=True, help_text="URL de Vimeo/Youtube")
    file = models.FileField(
        upload_to='course_materials/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'zip'])]
    )
    
    text_content = models.TextField(blank=True, help_text="Descripción o contenido texto")
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
    def get_youtube_embed_url(self):
        """Extrae el ID del video de YouTube y devuelve la URL de embed"""
        if not self.video_url:
            return None
        
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^?]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([^?]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([^?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.video_url)
            if match:
                video_id = match.group(1)
                # Agregar parámetros para evitar restricciones
                return f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0&modestbranding=1"
        
        return None
    
    def get_vimeo_embed_url(self):
        """Extrae el ID del video de Vimeo y devuelve la URL de embed"""
        if not self.video_url:
            return None
        
        pattern = r'(?:https?://)?(?:www\.)?vimeo\.com/(\d+)'
        match = re.search(pattern, self.video_url)
        
        if match:
            video_id = match.group(1)
            return f"https://player.vimeo.com/video/{video_id}"
        
        return None

class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'lesson']
        verbose_name_plural = 'User Progress'
    
    def __str__(self):
        status = "✓" if self.is_completed else "✗"
        return f"{self.user.username} - {self.lesson.title} [{status}]"


class CourseReview(models.Model):
    """
    Modelo para reseñas/comentarios de cursos.
    Permite a los estudiantes calificar y comentar sobre los cursos.
    Un usuario puede dejar múltiples comentarios en un curso.
    """
    RATING_CHOICES = (
        (1, '1 - Muy malo'),
        (2, '2 - Malo'),
        (3, '3 - Regular'),
        (4, '4 - Bueno'),
        (5, '5 - Excelente'),
    )
    
    course = models.ForeignKey(Course, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField(help_text="Comparte tu experiencia con este curso")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created']
        verbose_name = 'Course Review'
        verbose_name_plural = 'Course Reviews'
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating}/5)"

