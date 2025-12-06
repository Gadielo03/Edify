from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


ModuleFormSet = inlineformset_factory(
    parent_model=Course,
    model=Module,
    form=ModuleForm,
    fields=['title', 'order'],
    extra=1,
    can_delete=True
)