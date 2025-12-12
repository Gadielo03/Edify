from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='list'),
    path('create/', views.CourseCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.CourseDeleteView.as_view(), name='delete'),
    path('lesson/<int:lesson_id>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', views.MarkLessonCompleteView.as_view(), name='mark_complete'),
]
