# gestion_notes/models.py
"""
MODULE 3 : Gestion des Notes - Models
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.gestion_academique.models import Etudiant, Enseignant
from apps.structure_pedagogique.models import Matiere, Semestre


class UniteEnseignement(models.Model):
    """Unité d'Enseignement (UE) - regroupement de matières"""
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    nom = models.CharField(max_length=200, verbose_name="Nom de l'UE")
    semestre = models.ForeignKey(
        Semestre,
        on_delete=models.PROTECT,
        related_name='unites',
        verbose_name="Semestre"
    )
    matieres = models.ManyToManyField(
        Matiere,
        related_name='unites',
        verbose_name="Matières"
    )

    class Meta:
        verbose_name = "Unité d'Enseignement"
        verbose_name_plural = "Unités d'Enseignement"
        ordering = ['semestre__ordre', 'code']

    def __str__(self):
        return f"{self.code} - {self.nom} ({self.semestre.code})"

    def get_matieres(self):
        """Retourne la liste des matières de l'UE"""
        return self.matieres.all()

    def calculer_moyenne_ue(self, etudiant):
        """
        Calcule la moyenne de l'UE pour un étudiant
        Moyenne UE = somme(moyenne_matiere * coefficient) / somme(coefficients)
        """
        total_points = 0
        total_coef = 0

        for matiere in self.matieres.all():
            try:
                note = Note.objects.get(
                    etudiant=etudiant,
                    matiere=matiere,
                    statut='valide'
                )
                total_points += note.moyenne * matiere.coefficient
                total_coef += matiere.coefficient
            except Note.DoesNotExist:
                # Si pas de note validée, on ignore
                pass

        if total_coef > 0:
            return round(total_points / total_coef, 2)
        return 0.0

    def get_resultat(self, etudiant):
        """Retourne le résultat de l'UE pour un étudiant"""
        moyenne = self.calculer_moyenne_ue(etudiant)
        if moyenne >= 5:
            return 'admis'
        elif moyenne >= 3:
            return 'session'
        else:
            return 'dette'
    def get_note_litterale_ue(self, etudiant):
    
        moyenne = self.calculer_moyenne_ue(etudiant)
        
        if moyenne >= 9.00:
            return 'A+'
        elif moyenne >= 8.51:
            return 'A'
        elif moyenne >= 8.00:
            return 'A-'
        elif moyenne >= 7.60:
            return 'B+'
        elif moyenne >= 7.40:
            return 'B'
        elif moyenne >= 7.00:
            return 'B-'
        elif moyenne >= 6.60:
            return 'C+'
        elif moyenne >= 6.40:
            return 'C'
        elif moyenne >= 6.00:
            return 'C-'
        elif moyenne >= 5.60:
            return 'D+'
        elif moyenne >= 5.40:
            return 'D'
        elif moyenne >= 5.00:
            return 'D-'
        else:
            return 'E'

    def est_valide_ue(self, etudiant):
        """UE validée si moyenne >= 5"""
        return self.calculer_moyenne_ue(etudiant) >= 5.00


class Note(models.Model):
    """Note d'un étudiant pour une matière"""

    STATUT_CHOICES = (
        ('brouillon', 'Brouillon'),      # Enseignant saisi mais pas soumis
        ('soumis', 'Soumis'),            # Enseignant a soumis au chef
        ('valide', 'Validé'),            # Chef a validé
        ('invalide', 'Invalidé'),        # Chef a invalidé → enseignant peut modifier
    )

    etudiant = models.ForeignKey(
        Etudiant,
        on_delete=models.PROTECT,
        related_name='notes',
        verbose_name="Étudiant"
    )
    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.PROTECT,
        related_name='notes',
        verbose_name="Matière"
    )
    enseignant = models.ForeignKey(
        Enseignant,
        on_delete=models.PROTECT,
        related_name='notes',
        verbose_name="Enseignant"
    )

    # Les 3 notes (sur 10)
    note1 = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Note 1",
        null=True, blank=True
    )
    note2 = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Note 2",
        null=True, blank=True
    )
    note3 = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Note 3",
        null=True, blank=True
    )

    # Moyenne calculée automatiquement
    moyenne = models.FloatField(
        default=0.0,
        editable=False,
        verbose_name="Moyenne"
    )

    # Statut du workflow
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='brouillon',
        verbose_name="Statut"
    )

    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_soumission = models.DateTimeField(null=True, blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        unique_together = ['etudiant', 'matiere']
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.etudiant.get_full_name()} - {self.matiere.nom} : {self.moyenne}/10"

    def calculer_moyenne(self):
        """
        Calcule la moyenne :
        Note1 × 0.3 + Note2 × 0.3 + Note3 × 0.4
        """
        n1 = self.note1 or 0
        n2 = self.note2 or 0
        n3 = self.note3 or 0
        self.moyenne = round((n1 * 0.3) + (n2 * 0.3) + (n3 * 0.4), 2)

    def save(self, *args, **kwargs):
        """Calcule la moyenne avant de sauvegarder"""
        self.calculer_moyenne()
        super().save(*args, **kwargs)

    def get_resultat(self):
        """Retourne le résultat selon la moyenne"""
        if self.moyenne >= 5:
            return 'admis'
        elif self.moyenne >= 3:
            return 'session'
        else:
            return 'dette'

    def get_resultat_display_custom(self):
        """Retourne le texte du résultat"""
        resultat = self.get_resultat()
        if resultat == 'admis':
            return 'Admis'
        elif resultat == 'session':
            return 'Session'
        else:
            return 'Dette'

    # ===== WORKFLOW =====

    def peut_modifier(self):
        """L'enseignant peut modifier si brouillon ou invalide"""
        return self.statut in ['brouillon', 'invalide']

    def peut_soumettre(self):
        """L'enseignant peut soumettre si brouillon ou invalide"""
        return self.statut in ['brouillon', 'invalide']

    def peut_valider(self):
        """Le chef peut valider si soumis"""
        return self.statut == 'soumis'

    def peut_invalider(self):
        """Le chef peut invalider si soumis ou validé"""
        return self.statut in ['soumis', 'valide']
    def get_note_litterale(self):

        if self.moyenne >= 9.00:
            return 'A+'
        elif self.moyenne >= 8.51:
            return 'A'
        elif self.moyenne >= 8.00:
            return 'A-'
        elif self.moyenne >= 7.60:
            return 'B+'
        elif self.moyenne >= 7.40:
            return 'B'
        elif self.moyenne >= 7.00:
            return 'B-'
        elif self.moyenne >= 6.60:
            return 'C+'
        elif self.moyenne >= 6.40:
            return 'C'
        elif self.moyenne >= 6.00:
            return 'C-'
        elif self.moyenne >= 5.60:
            return 'D+'
        elif self.moyenne >= 5.40:
            return 'D'
        elif self.moyenne >= 5.00:
            return 'D-'
        else:
            return 'F'

    def est_valide(self):
        """Une note est validée si moyenne >= 5"""
        return self.moyenne >= 5.