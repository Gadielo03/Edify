from django.contrib import admin
from .models import Course, Module, Lesson, UserProgress, CourseReview

# Register your models here.

@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'rating', 'created', 'updated']
    list_filter = ['rating', 'created']
    search_fields = ['user__username', 'course__title', 'comment']
    readonly_fields = ['created', 'updated']
