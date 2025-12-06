from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

class Course(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='courses_created', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
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

class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'lesson']