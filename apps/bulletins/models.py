# bulletins/models.py
"""
MODULE 5 : Bulletins & Délibérations - Models
Fichier : apps/bulletins/models.py
"""
from django.db import models
from apps.gestion_academique.models import Etudiant, AnneeAcademique
from apps.structure_pedagogique.models import Semestre
from apps.gestion_notes.models import Note


class Resultat(models.Model):
    """Résultat d'un étudiant pour un semestre"""
    DECISION_CHOICES = (
        ('admis', 'Admis'),
        ('ajourne', 'Ajourné'),
    )
    
    etudiant = models.ForeignKey(
        Etudiant,
        on_delete=models.CASCADE,
        related_name='resultats',
        verbose_name="Étudiant"
    )
    semestre = models.ForeignKey(
        Semestre,
        on_delete=models.PROTECT,
        related_name='resultats',
        verbose_name="Semestre"
    )
    annee_academique = models.ForeignKey(
        AnneeAcademique,
        on_delete=models.PROTECT,
        related_name='resultats',
        verbose_name="Année académique"
    )
    
    moyenne_generale = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        verbose_name="Moyenne générale (/10)"
    )
    total_credits_obtenus = models.IntegerField(default=0, verbose_name="Crédits obtenus")
    total_credits_requis = models.IntegerField(default=0, verbose_name="Crédits requis")
    
    decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        default='ajourne',
        verbose_name="Décision"
    )
    observation = models.TextField(blank=True, verbose_name="Observation")
    
    genere_le = models.DateTimeField(auto_now_add=True, verbose_name="Généré le")
    
    class Meta:
        verbose_name = "Résultat"
        verbose_name_plural = "Résultats"
        ordering = ['-genere_le']
        unique_together = ['etudiant', 'semestre', 'annee_academique']
    
    def __str__(self):
        return f"{self.etudiant} - {self.semestre} {self.annee_academique} - {self.get_decision_display()}"
    
    def calculer_moyenne(self):
        """Calcule la moyenne générale pondérée par les coefficients"""
        notes = Note.objects.filter(
            etudiant=self.etudiant,
            matiere__semestre=self.semestre,
            statut='valide'
        )
        
        if not notes.exists():
            self.moyenne_generale = 0
            return 0
        
        somme_notes_ponderees = sum(note.moyenne() * note.matiere.coefficient for note in notes)
        somme_coefficients = sum(note.matiere.coefficient for note in notes)
        
        if somme_coefficients > 0:
            self.moyenne_generale = round(somme_notes_ponderees / somme_coefficients, 2)
        else:
            self.moyenne_generale = 0
        
        return self.moyenne_generale
    
    def calculer_credits(self):
        """Calcule le total des crédits obtenus et requis"""
        notes = Note.objects.filter(
            etudiant=self.etudiant,
            matiere__semestre=self.semestre,
            statut='valide'
        )
        
        self.total_credits_requis = sum(note.matiere.credits for note in notes)
        self.total_credits_obtenus = sum(
            note.matiere.credits for note in notes if note.est_admis()
        )
        
        return self.total_credits_obtenus
    
    def determiner_decision(self):
        """Détermine si l'étudiant est admis ou ajourné (moyenne >= 5)"""
        if self.moyenne_generale >= 5:
            self.decision = 'admis'
        else:
            self.decision = 'ajourne'
        
        return self.decision
    
    def get_decision_color(self):
        """Retourne la couleur pour l'affichage de la décision"""
        if self.decision == 'admis':
            return 'success'
        return 'danger'


class Bulletin(models.Model):
    """Bulletin de notes PDF"""
    resultat = models.OneToOneField(
        Resultat,
        on_delete=models.CASCADE,
        related_name='bulletin',
        verbose_name="Résultat"
    )
    fichier_pdf = models.FileField(
        upload_to='bulletins/',
        null=True,
        blank=True,
        verbose_name="Fichier PDF"
    )
    
    genere_le = models.DateTimeField(auto_now_add=True, verbose_name="Généré le")
    telecharge_le = models.DateTimeField(null=True, blank=True, verbose_name="Téléchargé le")
    nombre_telechargements = models.IntegerField(default=0, verbose_name="Nombre de téléchargements")
    
    class Meta:
        verbose_name = "Bulletin"
        verbose_name_plural = "Bulletins"
        ordering = ['-genere_le']
    
    def __str__(self):
        return f"Bulletin - {self.resultat.etudiant} - {self.resultat.semestre}"
    
    def incrementer_telechargements(self):
        """Incrémente le compteur de téléchargements"""
        from django.utils import timezone
        self.nombre_telechargements += 1
        self.telecharge_le = timezone.now()
        self.save()
