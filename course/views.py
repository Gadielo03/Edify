from django.shortcuts import render
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from .models import Lesson, UserProgress

class MarkLessonCompleteView(View):
    def post(self, request, *args, **kwargs):
        lesson_id = kwargs.get('pk')
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        progress.is_completed = True
        progress.save()
        
        return redirect('course_detail', slug=lesson.module.course.slug)