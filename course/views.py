from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db import transaction
from .models import Course, Module, Lesson, UserProgress, CourseReview
from .forms import CourseForm, ModuleFormSet, LessonFormSet, CourseReviewForm


class CourseListView(ListView):
    """Vista para listar todos los cursos disponibles"""
    model = Course
    template_name = 'course/course_list.html'
    context_object_name = 'courses'
    ordering = ['-created']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Verificar si el usuario es maestro
        if self.request.user.is_authenticated:
            context['is_teacher'] = self.request.user.is_teacher
        else:
            context['is_teacher'] = False
        return context


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para crear un nuevo curso con módulos y lecciones"""
    
    def test_func(self):
        """Solo los maestros pueden crear cursos"""
        return self.request.user.is_teacher
    
    def handle_no_permission(self):
        messages.error(self.request, 'Solo los maestros pueden crear cursos.')
        return redirect('course:list')
    
    def get(self, request):
        course_form = CourseForm()
        context = {
            'course_form': course_form,
        }
        return render(request, 'course/course_create.html', context)
    
    @transaction.atomic
    def post(self, request):
        course_form = CourseForm(request.POST)
        
        if course_form.is_valid():
            # Guardar el curso
            course = course_form.save(commit=False, owner=request.user)
            course.save()
            
            # Procesar módulos y lecciones desde los datos del formulario
            modules_data = self._extract_modules_data(request.POST, request.FILES)
            
            if not modules_data:
                messages.error(request, 'Debes agregar al menos un módulo con una lección.')
                course.delete()
                return self.get(request)
            
            # Crear módulos y lecciones
            for module_data in modules_data:
                module = Module.objects.create(
                    course=course,
                    title=module_data['title'],
                    order=module_data['order']
                )
                
                for lesson_data in module_data['lessons']:
                    Lesson.objects.create(
                        module=module,
                        title=lesson_data['title'],
                        content_type=lesson_data['content_type'],
                        video_url=lesson_data.get('video_url', ''),
                        file=lesson_data.get('file'),
                        text_content=lesson_data.get('text_content', ''),
                        order=lesson_data['order']
                    )
            
            messages.success(request, f'¡Curso "{course.title}" creado exitosamente!')
            return redirect('course:list')
        
        context = {
            'course_form': course_form,
        }
        return render(request, 'course/course_create.html', context)
    
    def _extract_modules_data(self, post_data, files_data):
        """Extrae los datos de módulos y lecciones del POST"""
        modules = {}
        
        # Extraer módulos
        for key, value in post_data.items():
            if key.startswith('module_') and '_title' in key:
                module_index = key.split('_')[1]
                if module_index not in modules:
                    modules[module_index] = {
                        'title': value,
                        'order': int(post_data.get(f'module_{module_index}_order', 1)),
                        'lessons': {}
                    }
        
        # Extraer lecciones para cada módulo
        for key, value in post_data.items():
            if key.startswith('module_') and '_lesson_' in key:
                parts = key.split('_')
                module_index = parts[1]
                lesson_index = parts[3]
                field_name = '_'.join(parts[4:])
                
                if module_index in modules:
                    if lesson_index not in modules[module_index]['lessons']:
                        modules[module_index]['lessons'][lesson_index] = {}
                    
                    modules[module_index]['lessons'][lesson_index][field_name] = value
        
        # Agregar archivos
        for key, file_obj in files_data.items():
            if key.startswith('module_') and '_lesson_' in key and '_file' in key:
                parts = key.split('_')
                module_index = parts[1]
                lesson_index = parts[3]
                
                if module_index in modules and lesson_index in modules[module_index]['lessons']:
                    modules[module_index]['lessons'][lesson_index]['file'] = file_obj
        
        # Convertir a lista
        result = []
        for module_data in modules.values():
            lessons_list = []
            for lesson_data in module_data['lessons'].values():
                if lesson_data.get('title'):  # Solo agregar lecciones con título
                    lessons_list.append(lesson_data)
            
            if lessons_list:  # Solo agregar módulos con lecciones
                module_data['lessons'] = lessons_list
                result.append(module_data)
        
        return result


class CourseDetailView(LoginRequiredMixin, View):
    """Vista para mostrar el detalle del curso con módulos y lecciones"""
    
    def get(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        modules = course.modules.prefetch_related('lessons').all()
        
        # Obtener progreso del usuario
        user_progress = {}
        completed_lessons = UserProgress.objects.filter(
            user=request.user,
            lesson__module__course=course,
            is_completed=True
        ).values_list('lesson_id', flat=True)
        
        # Crear estructura de datos con información de desbloqueo
        modules_data = []
        previous_lesson_completed = True
        
        for module in modules:
            lessons_data = []
            for lesson in module.lessons.all():
                is_completed = lesson.id in completed_lessons
                is_unlocked = previous_lesson_completed
                
                lessons_data.append({
                    'lesson': lesson,
                    'is_completed': is_completed,
                    'is_unlocked': is_unlocked,
                })
                
                # La siguiente lección solo estará desbloqueada si esta está completada
                previous_lesson_completed = is_completed
            
            modules_data.append({
                'module': module,
                'lessons': lessons_data,
            })
        
        # Calcular progreso general
        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_count = len(completed_lessons)
        progress_percentage = (completed_count / total_lessons * 100) if total_lessons > 0 else 0
        
        # Obtener reviews del curso
        reviews = course.reviews.select_related('user').all()
        
        # Calcular calificación promedio
        if reviews:
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
        else:
            avg_rating = 0
        
        # Formulario para nueva review
        review_form = CourseReviewForm()
        review_form.helper.form_action = reverse('course:review_create', kwargs={'slug': course.slug})
        
        context = {
            'course': course,
            'modules_data': modules_data,
            'progress_percentage': round(progress_percentage, 1),
            'completed_count': completed_count,
            'total_lessons': total_lessons,
            'is_teacher': request.user.is_teacher,
            'is_owner': course.owner == request.user,
            'reviews': reviews,
            'avg_rating': round(avg_rating, 1),
            'review_form': review_form,
        }
        
        return render(request, 'course/course_detail.html', context)


class LessonDetailView(LoginRequiredMixin, View):
    """Vista para mostrar el detalle de una lección"""
    
    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        course = lesson.module.course
        
        # Verificar si la lección está desbloqueada
        if not self._is_lesson_unlocked(request.user, lesson):
            messages.warning(request, 'Debes completar las lecciones anteriores primero.')
            return redirect('course:detail', slug=course.slug)
        
        # Verificar si está completada
        is_completed = UserProgress.objects.filter(
            user=request.user,
            lesson=lesson,
            is_completed=True
        ).exists()
        
        # Obtener lección anterior y siguiente
        all_lessons = Lesson.objects.filter(module__course=course).order_by('module__order', 'order')
        lesson_list = list(all_lessons)
        current_index = lesson_list.index(lesson)
        
        previous_lesson = lesson_list[current_index - 1] if current_index > 0 else None
        next_lesson = lesson_list[current_index + 1] if current_index < len(lesson_list) - 1 else None
        
        # Verificar si la siguiente lección está desbloqueada
        next_lesson_unlocked = False
        if next_lesson:
            next_lesson_unlocked = self._is_lesson_unlocked(request.user, next_lesson)
        
        context = {
            'lesson': lesson,
            'course': course,
            'module': lesson.module,
            'is_completed': is_completed,
            'previous_lesson': previous_lesson,
            'next_lesson': next_lesson,
            'next_lesson_unlocked': next_lesson_unlocked,
        }
        
        return render(request, 'course/lesson_detail.html', context)
    
    def _is_lesson_unlocked(self, user, lesson):
        """Verifica si una lección está desbloqueada para el usuario"""
        course = lesson.module.course
        all_lessons = Lesson.objects.filter(module__course=course).order_by('module__order', 'order')
        
        for les in all_lessons:
            if les == lesson:
                return True
            
            # Si encontramos una lección no completada antes de la actual, está bloqueada
            is_completed = UserProgress.objects.filter(
                user=user,
                lesson=les,
                is_completed=True
            ).exists()
            
            if not is_completed:
                return False
        
        return True


class MarkLessonCompleteView(LoginRequiredMixin, View):
    """Vista para marcar una lección como completada"""
    
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        
        # Verificar si la lección está desbloqueada
        if not self._is_lesson_unlocked(request.user, lesson):
            messages.error(request, 'No puedes completar esta lección aún.')
            return redirect('course:detail', slug=lesson.module.course.slug)
        
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        progress.is_completed = True
        progress.save()
        
        messages.success(request, f'¡Lección "{lesson.title}" completada!')
        
        # Redirigir a la siguiente lección si existe
        all_lessons = Lesson.objects.filter(
            module__course=lesson.module.course
        ).order_by('module__order', 'order')
        
        lesson_list = list(all_lessons)
        current_index = lesson_list.index(lesson)
        
        if current_index < len(lesson_list) - 1:
            next_lesson = lesson_list[current_index + 1]
            return redirect('course:lesson_detail', lesson_id=next_lesson.id)
        else:
            messages.success(request, '¡Felicitaciones! Has completado el curso.')
            return redirect('course:detail', slug=lesson.module.course.slug)
    
    def _is_lesson_unlocked(self, user, lesson):
        """Verifica si una lección está desbloqueada para el usuario"""
        course = lesson.module.course
        all_lessons = Lesson.objects.filter(module__course=course).order_by('module__order', 'order')
        
        for les in all_lessons:
            if les == lesson:
                return True
            
            is_completed = UserProgress.objects.filter(
                user=user,
                lesson=les,
                is_completed=True
            ).exists()
            
            if not is_completed:
                return False
        
        return True


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para editar un curso existente con módulos y lecciones"""
    
    def test_func(self):
        """Solo el propietario del curso puede editarlo"""
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        return self.request.user == course.owner
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permiso para editar este curso.')
        return redirect('course:list')
    
    def get(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        course_form = CourseForm(instance=course)
        
        # Obtener módulos y lecciones existentes
        modules = course.modules.prefetch_related('lessons').all()
        
        # Preparar datos para JavaScript
        import json
        modules_data = []
        for module in modules:
            lessons_data = []
            for lesson in module.lessons.all():
                lessons_data.append({
                    'id': lesson.id,
                    'title': lesson.title,
                    'content_type': lesson.content_type,
                    'video_url': lesson.video_url or '',
                    'text_content': lesson.text_content or '',
                    'order': lesson.order,
                    'file_url': lesson.file.url if lesson.file else '',
                    'file_name': lesson.file.name.split('/')[-1] if lesson.file else '',
                })
            modules_data.append({
                'id': module.id,
                'title': module.title,
                'order': module.order,
                'lessons': lessons_data,
            })
        
        context = {
            'course': course,
            'course_form': course_form,
            'modules': json.dumps(modules_data),
            'is_edit': True,
        }
        return render(request, 'course/course_edit.html', context)
    
    @transaction.atomic
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        course_form = CourseForm(request.POST, instance=course)
        
        if course_form.is_valid():
            course = course_form.save()
            
            # Procesar módulos y lecciones desde los datos del formulario
            modules_data = self._extract_modules_data(request.POST, request.FILES)
            
            if not modules_data:
                messages.error(request, 'Debes tener al menos un módulo con una lección.')
                return self.get(request, slug)
            
            # Obtener IDs de módulos existentes que fueron enviados
            existing_module_ids = set()
            for key in request.POST.keys():
                if key.startswith('module_id_'):
                    module_index = key.split('_')[2]
                    module_id = request.POST.get(key)
                    if module_id:
                        existing_module_ids.add(int(module_id))
            
            # Eliminar módulos que no están en el formulario (fueron eliminados)
            course.modules.exclude(id__in=existing_module_ids).delete()
            
            # Procesar cada módulo
            for module_data in modules_data:
                module_id = module_data.get('id')
                
                if module_id:
                    # Actualizar módulo existente
                    module = Module.objects.get(id=module_id, course=course)
                    module.title = module_data['title']
                    module.order = module_data['order']
                    module.save()
                else:
                    # Crear nuevo módulo
                    module = Module.objects.create(
                        course=course,
                        title=module_data['title'],
                        order=module_data['order']
                    )
                
                # Obtener IDs de lecciones existentes para este módulo
                existing_lesson_ids = set()
                for lesson_data in module_data['lessons']:
                    if lesson_data.get('id'):
                        existing_lesson_ids.add(int(lesson_data['id']))
                
                # Eliminar lecciones que no están en el formulario
                module.lessons.exclude(id__in=existing_lesson_ids).delete()
                
                # Procesar lecciones
                for lesson_data in module_data['lessons']:
                    lesson_id = lesson_data.get('id')
                    
                    if lesson_id:
                        # Actualizar lección existente
                        lesson = Lesson.objects.get(id=lesson_id, module=module)
                        lesson.title = lesson_data['title']
                        lesson.content_type = lesson_data['content_type']
                        lesson.video_url = lesson_data.get('video_url', '')
                        lesson.text_content = lesson_data.get('text_content', '')
                        lesson.order = lesson_data['order']
                        
                        # Actualizar archivo si se subió uno nuevo
                        if lesson_data.get('file'):
                            lesson.file = lesson_data['file']
                        
                        lesson.save()
                    else:
                        # Crear nueva lección
                        Lesson.objects.create(
                            module=module,
                            title=lesson_data['title'],
                            content_type=lesson_data['content_type'],
                            video_url=lesson_data.get('video_url', ''),
                            file=lesson_data.get('file'),
                            text_content=lesson_data.get('text_content', ''),
                            order=lesson_data['order']
                        )
            
            messages.success(request, f'Curso "{course.title}" actualizado exitosamente!')
            return redirect('course:detail', slug=course.slug)
        
        # Si el formulario no es válido, volver a cargar
        modules = course.modules.prefetch_related('lessons').all()
        context = {
            'course': course,
            'course_form': course_form,
            'modules': modules,
            'is_edit': True,
        }
        return render(request, 'course/course_edit.html', context)
    
    def _extract_modules_data(self, post_data, files_data):
        """Extrae los datos de módulos y lecciones del POST"""
        modules = {}
        
        # Extraer módulos
        for key, value in post_data.items():
            if key.startswith('module_') and '_title' in key:
                module_index = key.split('_')[1]
                if module_index not in modules:
                    modules[module_index] = {
                        'id': post_data.get(f'module_id_{module_index}'),
                        'title': value,
                        'order': int(post_data.get(f'module_{module_index}_order', 1)),
                        'lessons': {}
                    }
        
        # Extraer lecciones para cada módulo
        for key, value in post_data.items():
            if key.startswith('module_') and '_lesson_' in key:
                parts = key.split('_')
                module_index = parts[1]
                lesson_index = parts[3]
                field_name = '_'.join(parts[4:])
                
                if module_index in modules:
                    if lesson_index not in modules[module_index]['lessons']:
                        modules[module_index]['lessons'][lesson_index] = {}
                    
                    modules[module_index]['lessons'][lesson_index][field_name] = value
        
        # Agregar archivos
        for key, file_obj in files_data.items():
            if key.startswith('module_') and '_lesson_' in key and '_file' in key:
                parts = key.split('_')
                module_index = parts[1]
                lesson_index = parts[3]
                
                if module_index in modules and lesson_index in modules[module_index]['lessons']:
                    modules[module_index]['lessons'][lesson_index]['file'] = file_obj
        
        # Convertir a lista
        result = []
        for module_data in modules.values():
            lessons_list = []
            for lesson_data in module_data['lessons'].values():
                if lesson_data.get('title'):
                    lessons_list.append(lesson_data)
            
            if lessons_list:
                module_data['lessons'] = lessons_list
                result.append(module_data)
        
        return result


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para eliminar un curso"""
    
    def test_func(self):
        """Solo el propietario del curso puede eliminarlo"""
        course = get_object_or_404(Course, slug=self.kwargs['slug'])
        return self.request.user == course.owner
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permiso para eliminar este curso.')
        return redirect('course:list')
    
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        course_title = course.title
        
        # Eliminar el curso (cascada eliminará módulos, lecciones y progreso)
        course.delete()
        
        messages.success(request, f'Curso "{course_title}" eliminado exitosamente.')
        return redirect('course:list')


class CourseReviewCreateView(LoginRequiredMixin, View):
    """Vista para crear una nueva reseña de curso"""
    
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        form = CourseReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.course = course
            review.user = request.user
            review.save()
            
            messages.success(request, '¡Comentario publicado exitosamente!')
        else:
            messages.error(request, 'Error al publicar el comentario. Por favor verifica los datos.')
        
        return redirect('course:detail', slug=slug)


class CourseReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para editar una reseña existente"""
    
    def test_func(self):
        """Solo el autor de la reseña puede editarla"""
        review = get_object_or_404(CourseReview, id=self.kwargs['review_id'])
        return self.request.user == review.user
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permiso para editar este comentario.')
        return redirect('course:detail', slug=self.kwargs['slug'])
    
    def get(self, request, slug, review_id):
        course = get_object_or_404(Course, slug=slug)
        review = get_object_or_404(CourseReview, id=review_id)
        form = CourseReviewForm(instance=review)
        
        context = {
            'course': course,
            'form': form,
            'review': review,
            'is_edit': True,
        }
        return render(request, 'course/review_form.html', context)
    
    def post(self, request, slug, review_id):
        review = get_object_or_404(CourseReview, id=review_id)
        form = CourseReviewForm(request.POST, instance=review)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Comentario actualizado exitosamente.')
            return redirect('course:detail', slug=slug)
        
        course = get_object_or_404(Course, slug=slug)
        context = {
            'course': course,
            'form': form,
            'review': review,
            'is_edit': True,
        }
        return render(request, 'course/review_form.html', context)


class CourseReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Vista para eliminar una reseña"""
    
    def test_func(self):
        """Solo el autor de la reseña puede eliminarla"""
        review = get_object_or_404(CourseReview, id=self.kwargs['review_id'])
        return self.request.user == review.user
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permiso para eliminar este comentario.')
        return redirect('course:detail', slug=self.kwargs['slug'])
    
    def post(self, request, slug, review_id):
        review = get_object_or_404(CourseReview, id=review_id)
        review.delete()
        
        messages.success(request, 'Comentario eliminado exitosamente.')
        return redirect('course:detail', slug=slug)
