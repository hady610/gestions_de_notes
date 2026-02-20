# gestion_notes/forms.py
# gestion_notes/forms.py
"""
MODULE 3 : Gestion des Notes - Forms
"""
from django import forms
from .models import Note, UniteEnseignement


class NoteForm(forms.ModelForm):
    """Formulaire pour saisir les notes"""
    class Meta:
        model = Note
        fields = ['note1', 'note2', 'note3']
        widgets = {
            'note1': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10',
            #    'step': '0.5',
                'placeholder': '/10'
            }),
            'note2': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10',
            #    'step': '0.5',
                'placeholder': '/10'
            }),
            'note3': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10',
            #    'step': '0.5',
                'placeholder': '/10'
            }),
        }
        labels = {
            'note1': 'Note 1 (×0.3)',
            'note2': 'Note 2 (×0.3)',
            'note3': 'Note 3 (×0.4)',
        }


class UniteEnseignementForm(forms.ModelForm):
    """Formulaire pour créer une UE"""
    class Meta:
        model = UniteEnseignement
        fields = ['code', 'nom', 'semestre', 'matieres']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: UE1-S1'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Ex: Informatique Fondamentale"
            }),
            'semestre': forms.Select(attrs={
                'class': 'form-select'
            }),
            'matieres': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'code': 'Code UE',
            'nom': "Nom de l'UE",
            'semestre': 'Semestre',
            'matieres': 'Matières (1 à 5)',
        }