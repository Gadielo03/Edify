from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    IS_TEACHER = 'TEACHER'
    IS_STUDENT = 'STUDENT'
    
    ROLE_CHOICES = [
        (IS_TEACHER, 'Maestro'),
        (IS_STUDENT, 'Estudiante'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=IS_STUDENT)
    bio = models.TextField(blank=True)
    
    @property
    def is_teacher(self):
        return self.role == self.IS_TEACHER