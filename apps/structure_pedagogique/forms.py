"""
MODULE 4 : Structure Pédagogique - Forms
"""
from django import forms
from .models import Semestre, Matiere


class SemestreForm(forms.ModelForm):
    """Formulaire pour les semestres"""
    class Meta:
        model = Semestre
        fields = ['code', 'nom', 'niveau', 'ordre']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: S1'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Semestre 1'
            }),
            'niveau': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ordre': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10'
            }),
        }
        labels = {
            'code': 'Code du semestre',
            'nom': 'Nom du semestre',
            'niveau': 'Niveau',
            'ordre': 'Ordre'
        }


class MatiereForm(forms.ModelForm):
    """Formulaire pour les matières"""
    class Meta:
        model = Matiere
        fields = [
            'code', 'nom', 'coefficient', 'credits',
            'departements', 'niveau', 'semestre',
            'enseignants', 'description'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: INF101'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Programmation Python'
            }),
            'coefficient': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10',
                'step': '0.5'
            }),
            'credits': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10'
            }),
            'departements': forms.CheckboxSelectMultiple(),
            'niveau': forms.Select(attrs={
                'class': 'form-select'
            }),
            'semestre': forms.Select(attrs={
                'class': 'form-select'
            }),
            'enseignants': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de la matière (optionnel)'
            }),
        }
        labels = {
            'code': 'Code de la matière',
            'nom': 'Nom de la matière',
            'coefficient': 'Coefficient',
            'credits': 'Crédits',
            'departements': 'Départements',
            'niveau': 'Niveau',
            'semestre': 'Semestre',
            'enseignants': 'Enseignants',
            'description': 'Description'
        }