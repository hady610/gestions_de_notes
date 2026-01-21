# gestion_academique/models.py
"""
MODULE 2 : Gestion Académique - Models
Fichier : apps/gestion_academique/models.py
"""
from django.db import models
from django.core.validators import RegexValidator
from datetime import date


class Departement(models.Model):
    """Département (NTIC, Développement Logiciel)"""
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    nom = models.CharField(max_length=100, verbose_name="Nom du département")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.code} - {self.nom}"


class Niveau(models.Model):
    """Niveau d'études (L1, L2, L3)"""
    code = models.CharField(max_length=5, unique=True, verbose_name="Code")
    nom = models.CharField(max_length=50, verbose_name="Nom")
    ordre = models.IntegerField(default=1, verbose_name="Ordre")
    
    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"
        ordering = ['ordre']
    
    def __str__(self):
        return f"{self.code} - {self.nom}"


class AnneeAcademique(models.Model):
    """Année académique (2025-2026, etc.)"""
    annee = models.CharField(max_length=20, unique=True, verbose_name="Année")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    est_active = models.BooleanField(default=False, verbose_name="Active")
    
    class Meta:
        verbose_name = "Année académique"
        verbose_name_plural = "Années académiques"
        ordering = ['-date_debut']
    
    def __str__(self):
        return self.annee
    
    def save(self, *args, **kwargs):
        """Si cette année est active, désactive les autres"""
        if self.est_active:
            AnneeAcademique.objects.filter(est_active=True).update(est_active=False)
        super().save(*args, **kwargs)


class Etudiant(models.Model):
    """Étudiant"""
    SEXE_CHOICES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    )
    
    matricule = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Matricule",
        validators=[RegexValidator(r'^ETU-\d{4}-\d{3}$', 'Format: ETU-2025-001')]
    )
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    date_naissance = models.DateField(verbose_name="Date de naissance")
    lieu_naissance = models.CharField(max_length=100, verbose_name="Lieu de naissance")
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, verbose_name="Sexe")
    
    departement = models.ForeignKey(
        Departement, 
        on_delete=models.PROTECT, 
        related_name='etudiants',
        verbose_name="Département"
    )
    niveau = models.ForeignKey(
        Niveau, 
        on_delete=models.PROTECT, 
        related_name='etudiants',
        verbose_name="Niveau"
    )
    annee_academique = models.ForeignKey(
        AnneeAcademique, 
        on_delete=models.PROTECT, 
        related_name='etudiants',
        verbose_name="Année académique"
    )
    
    email = models.EmailField(blank=True, verbose_name="Email")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    photo = models.ImageField(upload_to='etudiants/', null=True, blank=True, verbose_name="Photo")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"
    
    def get_full_name(self):
        """Retourne le nom complet"""
        return f"{self.nom} {self.prenom}"
    
    def get_age(self):
        """Calcule l'âge de l'étudiant"""
        today = date.today()
        age = today.year - self.date_naissance.year
        if today.month < self.date_naissance.month or \
           (today.month == self.date_naissance.month and today.day < self.date_naissance.day):
            age -= 1
        return age


class Enseignant(models.Model):
    """Enseignant"""
    GRADES = (
        ('professeur', 'Professeur'),
        ('maitre_conf', 'Maître de Conférences'),
        ('assistant', 'Assistant'),
        ('charge_cours', 'Chargé de Cours'),
    )
    
    code = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Code",
        validators=[RegexValidator(r'^ENS-\d{3}$', 'Format: ENS-001')]
    )
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    grade = models.CharField(max_length=20, choices=GRADES, verbose_name="Grade")
    specialite = models.CharField(max_length=200, verbose_name="Spécialité")
    
    departements = models.ManyToManyField(
        Departement, 
        related_name='enseignants',
        verbose_name="Départements"
    )
    
    email = models.EmailField(verbose_name="Email")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    photo = models.ImageField(upload_to='enseignants/', null=True, blank=True, verbose_name="Photo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Enseignant"
        verbose_name_plural = "Enseignants"
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.code} - {self.get_grade_display()} {self.nom} {self.prenom}"
    
    def get_full_name(self):
        """Retourne le nom complet avec grade"""
        return f"{self.get_grade_display()} {self.nom} {self.prenom}"
