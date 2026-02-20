# structure_pedagogique/models.py
"""
MODULE 4 : Structure Pédagogique - Models
Fichier : apps/structure_pedagogique/models.py
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.gestion_academique.models import Niveau, Enseignant, Departement


class Semestre(models.Model):
    """Semestre (S1, S2, S3, S4, S5, S6)"""
    code = models.CharField(max_length=5, unique=True, verbose_name="Code")
    nom = models.CharField(max_length=50, verbose_name="Nom")
    ordre = models.IntegerField(default=1, verbose_name="Ordre")
    
    niveau = models.ForeignKey(
        Niveau,
        on_delete=models.PROTECT,
        related_name='semestres',
        verbose_name="Niveau"
    )
    
    class Meta:
        verbose_name = "Semestre"
        verbose_name_plural = "Semestres"
        ordering = ['niveau__ordre', 'ordre']
    
    def __str__(self):
        return f"{self.code} - {self.nom} ({self.niveau.code})"


class Matiere(models.Model):
    """Matière/Cours"""
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    nom = models.CharField(max_length=200, verbose_name="Nom de la matière")
    description = models.TextField(blank=True, verbose_name="Description")
    
    coefficient = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Coefficient"
    )
    credits = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Crédits"
    )
    
    # MULTI-CHOIX pour départements (ManyToManyField)
    departements = models.ManyToManyField(
        Departement,
        related_name='matieres',
        verbose_name="Départements"
    )
    
    niveau = models.ForeignKey(
        Niveau,
        on_delete=models.PROTECT,
        related_name='matieres',
        verbose_name="Niveau"
    )
    
    semestre = models.ForeignKey(
        Semestre,
        on_delete=models.PROTECT,
        related_name='matieres',
        verbose_name="Semestre"
    )
    
    enseignants = models.ManyToManyField(
        Enseignant,
        related_name='matieres',
        verbose_name="Enseignants"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ['niveau__ordre', 'semestre__ordre', 'nom']
        unique_together = ['code', 'niveau', 'semestre']
    
    def __str__(self):
        depts = ", ".join([d.code for d in self.departements.all()])
        return f"{self.code} - {self.nom} ({self.niveau.code} {self.semestre.code}) - {depts}"
    
    def get_enseignants_list(self):
        """Retourne la liste des enseignants séparés par des virgules"""
        return ", ".join([str(ens) for ens in self.enseignants.all()])
    
    def get_departements_list(self):
        """Retourne la liste des départements"""
        return ", ".join([d.nom for d in self.departements.all()])