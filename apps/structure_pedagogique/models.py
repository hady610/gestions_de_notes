# structure_pedagogique/models.py
"""
MODULE 4 : Structure Pédagogique - Models
Fichier : apps/structure_pedagogique/models.py
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.gestion_academique.models import Niveau, Enseignant


class Semestre(models.Model):
    """Semestre (S1, S2)"""
    code = models.CharField(max_length=5, unique=True, verbose_name="Code")
    nom = models.CharField(max_length=50, verbose_name="Nom")
    ordre = models.IntegerField(default=1, verbose_name="Ordre")
    
    class Meta:
        verbose_name = "Semestre"
        verbose_name_plural = "Semestres"
        ordering = ['ordre']
    
    def __str__(self):
        return f"{self.code} - {self.nom}"


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
        validators=[MinValueValidator(1), MaxValueValidator(15)],
        verbose_name="Crédits"
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
        return f"{self.code} - {self.nom} ({self.niveau.code} {self.semestre.code})"
    
    def get_enseignants_list(self):
        """Retourne la liste des enseignants séparés par des virgules"""
        return ", ".join([str(ens) for ens in self.enseignants.all()])
