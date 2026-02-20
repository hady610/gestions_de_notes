# gestion_academique/forms.py
"""
MODULE 2 : Gestion Académique - Forms
"""
from django import forms
from django.core.exceptions import ValidationError
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


# ============= MODIFIÉ : Nouvelle version pour génération auto =============
class AnneeAcademiqueForm(forms.ModelForm):
    """
    Formulaire pour les années académiques
    Le champ 'annee' est généré automatiquement donc pas dans le formulaire
    """
    class Meta:
        model = AnneeAcademique
        fields = ['date_debut', 'date_fin', 'est_active']  # ← CHANGÉ : 'annee' retiré
        widgets = {
            'date_debut': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'placeholder': 'Date de début (ex: 1er septembre)'
            }),
            'date_fin': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'placeholder': 'Date de fin (ex: 31 août)'
            }),
            'est_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'date_debut': 'Le nom de l\'année sera généré automatiquement (Ex: 2025-2026)',
            'est_active': 'Cocher pour activer cette année (désactive automatiquement les autres)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        if date_debut and date_fin:
            if date_fin <= date_debut:
                raise ValidationError("La date de fin doit être après la date de début !")
        
        return cleaned_data
# ============================================================================


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
                'placeholder': 'XXX-XXX-XXX-XXX',
                'maxlength': '15'  # 12 chiffres + 3 tirets
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


# ============= NOUVEAU : Formulaire de filtrage des notes =============
class NoteFilterForm(forms.Form):
    """
    Formulaire de filtrage pour les notes
    Utilisé par le chef de département
    """
    annee = forms.ModelChoiceField(
        queryset=AnneeAcademique.objects.all().order_by('-date_debut'),
        required=False,
        empty_label="-- Toutes les années --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    matricule = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par matricule'
        })
    )
    
    niveau = forms.ModelChoiceField(
        queryset=Niveau.objects.all().order_by('ordre'),
        required=False,
        empty_label="-- Tous les niveaux --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    statut = forms.ChoiceField(
        required=False,
        choices=[
            ('', '-- Tous les statuts --'),
            ('brouillon', 'Brouillon'),
            ('soumis', 'Soumis'),
            ('valide', 'Validé'),
            ('invalide', 'Invalidé'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

# apps/gestion_academique/forms.py - AJOUTER À LA FIN DU FICHIER



class ImportEtudiantsForm(forms.Form):
    """Formulaire pour importer des étudiants depuis Excel"""
    fichier_excel = forms.FileField(
        label='Fichier Excel',
        help_text='Format accepté : .xlsx ou .csv',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv'
        })
    )
    
    annee_academique = forms.ModelChoiceField(
        queryset=None,  # Sera défini dans la vue
        label='Année Académique',
        help_text='Les étudiants seront inscrits dans cette année',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.gestion_academique.models import AnneeAcademique
        self.fields['annee_academique'].queryset = AnneeAcademique.objects.all().order_by('-est_active', '-date_debut')
        self.fields['annee_academique'].initial = AnneeAcademique.objects.filter(est_active=True).first()