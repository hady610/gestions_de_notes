# gestion_academique/forms.py
"""
MODULE 2 : Gestion Académique - Forms
"""
from django import forms
from .models import Departement, Niveau, AnneeAcademique, Etudiant, Enseignant


class DepartementForm(forms.ModelForm):
    """Formulaire pour les départements"""
    class Meta:
        model = Departement
        fields = ['code', 'nom', 'description']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: NTIC'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom complet du département'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description (optionnel)'
            }),
        }
        labels = {
            'code': 'Code du département',
            'nom': 'Nom du département',
            'description': 'Description'
        }


class NiveauForm(forms.ModelForm):
    """Formulaire pour les niveaux"""
    class Meta:
        model = Niveau
        fields = ['code', 'nom', 'ordre']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: L1'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Licence 1'
            }),
            'ordre': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10'
            }),
        }


class AnneeAcademiqueForm(forms.ModelForm):
    """Formulaire pour les années académiques"""
    class Meta:
        model = AnneeAcademique
        fields = ['annee', 'date_debut', 'date_fin', 'est_active']
        widgets = {
            'annee': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '2025-2026'
            }),
            'date_debut': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'est_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'annee': 'Année académique',
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
            'est_active': 'Année active'
        }


class EtudiantForm(forms.ModelForm):
    """Formulaire pour les étudiants"""
    class Meta:
        model = Etudiant
        fields = [
            'matricule', 'nom', 'prenom', 'date_naissance', 'lieu_naissance',
            'sexe', 'departement', 'niveau', 'annee_academique',
            'email', 'telephone', 'photo', 'adresse'
        ]
        widgets = {
            'matricule': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ETU-2025-001'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de famille'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'date_naissance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'lieu_naissance': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ville de naissance'
            }),
            'sexe': forms.Select(attrs={
                'class': 'form-select'
            }),
            'departement': forms.Select(attrs={
                'class': 'form-select'
            }),
            'niveau': forms.Select(attrs={
                'class': 'form-select'
            }),
            'annee_academique': forms.Select(attrs={
                'class': 'form-select'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemple@ugac.edu.gn'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+224 XXX XX XX XX'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Adresse complète'
            }),
        }


class EnseignantForm(forms.ModelForm):
    """Formulaire pour les enseignants"""
    class Meta:
        model = Enseignant
        fields = [
            'code', 'nom', 'prenom', 'grade', 'specialite',
            'departements', 'email', 'telephone', 'photo'
        ]
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ENS-001'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de famille'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'grade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'specialite': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Programmation Web'
            }),
            'departements': forms.CheckboxSelectMultiple(),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemple@ugac.edu.gn'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+224 XXX XX XX XX'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }