# gestion_notes/models.py
"""
MODULE 3 : Gestion des Notes - Models
Fichier : apps/gestion_notes/models.py
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from apps.gestion_academique.models import Etudiant
from apps.structure_pedagogique.models import Matiere


class Note(models.Model):
    """Note d'un étudiant pour une matière"""
    STATUT_CHOICES = (
        ('brouillon', 'Brouillon'),
        ('valide', 'Validé'),
    )
    
    etudiant = models.ForeignKey(
        Etudiant,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name="Étudiant"
    )
    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.PROTECT,
        related_name='notes',
        verbose_name="Matière"
    )
    
    controle = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Note de contrôle (/10)"
    )
    examen = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Note d'examen (/10)"
    )
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='brouillon',
        verbose_name="Statut"
    )
    
    valide_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notes_validees',
        verbose_name="Validé par"
    )
    valide_le = models.DateTimeField(null=True, blank=True, verbose_name="Validé le")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ['etudiant__nom', 'etudiant__prenom', 'matiere__nom']
        unique_together = ['etudiant', 'matiere']
    
    def __str__(self):
        return f"{self.etudiant} - {self.matiere.code} - Moyenne: {self.moyenne()}"
    
    def moyenne(self):
        """Calcule la moyenne de la note"""
        return round((float(self.controle) + float(self.examen)) / 2, 2)
    
    def est_admis(self):
        """Vérifie si l'étudiant est admis (moyenne >= 5)"""
        return self.moyenne() >= 5
    
    def peut_modifier(self):
        """Vérifie si la note peut être modifiée"""
        return self.statut == 'brouillon'
    
    def get_statut_display_color(self):
        """Retourne la couleur pour l'affichage du statut"""
        if self.statut == 'valide':
            return 'success'
        return 'warning'
    
    def clean(self):
        """Validation des données"""
        from django.core.exceptions import ValidationError
        
        if self.controle < 0 or self.controle > 10:
            raise ValidationError("La note de contrôle doit être entre 0 et 10")
        
        if self.examen < 0 or self.examen > 10:
            raise ValidationError("La note d'examen doit être entre 0 et 10")
        
        if self.statut == 'valide' and not self.peut_modifier():
            raise ValidationError("Une note validée ne peut plus être modifiée")
