from django import forms
from django.forms.models import inlineformset_factory
from django.utils.text import slugify
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, ButtonHolder, Submit
from crispy_forms.bootstrap import FormActions
from .models import Course, Module, Lesson, CourseReview


class CourseForm(forms.ModelForm):
    """Formulario para crear/editar cursos"""
    
    class Meta:
        model = Course
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Introducción a Python'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe de qué trata el curso...'
            }),
        }
        labels = {
            'title': 'Título del Curso',
            'description': 'Descripción',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('title', css_class='mb-3'),
            Field('description', css_class='mb-3'),
        )
    
    def save(self, commit=True, owner=None):
        instance = super().save(commit=False)
        if owner:
            instance.owner = owner
        if not instance.slug:
            instance.slug = slugify(instance.title)
        if commit:
            instance.save()
        return instance


class ModuleForm(forms.ModelForm):
    """Formulario para módulos del curso"""
    
    class Meta:
        model = Module
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Fundamentos básicos'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
        }
        labels = {
            'title': 'Título del Módulo',
            'order': 'Orden',
        }


class LessonForm(forms.ModelForm):
    """Formulario para lecciones del módulo"""
    
    class Meta:
        model = Lesson
        fields = ['title', 'content_type', 'video_url', 'video_file', 'file', 'text_content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Variables y tipos de datos'
            }),
            'content_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/mp4,video/webm,video/ogg,video/quicktime,video/x-msvideo'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'text_content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Contenido de texto de la lección...'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
        }
        labels = {
            'title': 'Título de la Lección',
            'content_type': 'Tipo de Contenido',
            'video_url': 'URL del Video (YouTube/Vimeo)',
            'video_file': 'O sube un video desde tu PC',
            'file': 'Archivo (PDF/ZIP)',
            'text_content': 'Contenido de Texto',
            'order': 'Orden',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        video_url = cleaned_data.get('video_url')
        video_file = cleaned_data.get('video_file')
        file = cleaned_data.get('file')
        text_content = cleaned_data.get('text_content')
        
        if content_type == 'video':
            if not video_url and not video_file:
                raise forms.ValidationError('Para contenido de video, debes proporcionar una URL o subir un archivo de video.')
            if video_url and video_file:
                raise forms.ValidationError('Proporciona solo una opción: URL de video O archivo de video, no ambos.')
        
        if content_type == 'pdf' and not file:
            self.add_error('file', 'Debes subir un archivo para este tipo de contenido.')
        
        return cleaned_data


ModuleFormSet = inlineformset_factory(
    parent_model=Course,
    model=Module,
    form=ModuleForm,
    fields=['title', 'order'],
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

LessonFormSet = inlineformset_factory(
    parent_model=Module,
    model=Lesson,
    form=LessonForm,
    fields=['title', 'content_type', 'video_url', 'video_file', 'file', 'text_content', 'order'],
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class CourseReviewForm(forms.ModelForm):
    """Formulario para crear/editar reseñas de cursos"""
    
    class Meta:
        model = CourseReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(
                attrs={'class': 'form-check-input'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Comparte tu experiencia con este curso...'
            }),
        }
        labels = {
            'rating': 'Calificación',
            'comment': 'Comentario',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Div(
                Field('rating', template='bootstrap5/layout/radioselect_inline.html'),
                css_class='mb-3'
            ),
            Field('comment', css_class='mb-3'),
            FormActions(
                Submit('submit', 'Publicar Comentario', css_class='btn btn-primary'),
                css_class='text-end'
            )
        )
