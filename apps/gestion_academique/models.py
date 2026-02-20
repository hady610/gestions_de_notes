# gestion_academique/models.py - VERSION ÉTENDUE
"""
MODULE 2 : Gestion Académique - Models ÉTENDU
Ajout de :
- Archivage des étudiants sortants
- Gestion du passage automatique d'année
- Historique des notes par année
"""
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
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
    
    # Nouveau champ pour savoir si le passage d'année a été effectué
    passage_effectue = models.BooleanField(default=False, verbose_name="Passage d'année effectué")
    date_passage = models.DateTimeField(null=True, blank=True, verbose_name="Date du passage")
    
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
    
    @staticmethod
    def generer_nom_annee(date_creation):
        """
        Génère le nom de l'année académique selon le format YYYY-YYYY+1
        Ex: si date_creation = 1er septembre 2025 → "2025-2026"
        """
        annee_debut = date_creation.year
        annee_fin = annee_debut + 1
        return f"{annee_debut}-{annee_fin}"


class Etudiant(models.Model):
    """Étudiant"""
    SEXE_CHOICES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    )
    
    STATUT_CHOICES = (
        ('actif', 'Actif'),
        ('archive', 'Archivé'),
        ('diplome', 'Diplômé'),
    )
    
    matricule = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Matricule",
        validators=[RegexValidator(r'^\d{3}-\d{3}-\d{3}-\d{3}$', 'Format: XXX-XXX-XXX-XXX')]
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
        'AnneeAcademique', 
        on_delete=models.PROTECT, 
        related_name='etudiants',
        verbose_name="Année académique"
    )
    
    # NOUVEAU : Statut de l'étudiant
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='actif',
        verbose_name="Statut"
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


class EtudiantArchive(models.Model):
    """
    Archive des étudiants sortants (fin de L3)
    Permet de suivre les diplômés et non-diplômés
    """
    STATUT_DIPLOME_CHOICES = (
        ('diplome', 'Diplômé'),
        ('non_diplome', 'Non diplômé'),
    )
    
    etudiant = models.ForeignKey(
        Etudiant,
        on_delete=models.PROTECT,
        related_name='archives',
        verbose_name="Étudiant"
    )
    
    departement = models.ForeignKey(
        Departement,
        on_delete=models.PROTECT,
        related_name='archives',
        verbose_name="Département"
    )
    
    annee_sortie = models.ForeignKey(
        AnneeAcademique,
        on_delete=models.PROTECT,
        related_name='sortants',
        verbose_name="Année de sortie"
    )
    
    statut_diplome = models.CharField(
        max_length=20,
        choices=STATUT_DIPLOME_CHOICES,
        verbose_name="Statut diplôme"
    )
    
    # Informations sur les UE manquantes pour les non-diplômés
    ue_manquantes = models.TextField(
        blank=True,
        verbose_name="UE manquantes (JSON)",
        help_text="Liste des codes UE non validées"
    )
    
    date_archivage = models.DateTimeField(auto_now_add=True, verbose_name="Date d'archivage")
    date_derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    
    class Meta:
        verbose_name = "Étudiant archivé"
        verbose_name_plural = "Étudiants archivés"
        ordering = ['-date_archivage']
        unique_together = ['etudiant', 'annee_sortie']
    
    def __str__(self):
        return f"{self.etudiant.get_full_name()} - {self.get_statut_diplome_display()} ({self.annee_sortie.annee})"
    
    def verifier_et_maj_statut(self):
        """
        Vérifie si l'étudiant a validé toutes les UE manquantes
        et met à jour automatiquement le statut vers "diplômé" si c'est le cas
        """
        if self.statut_diplome == 'diplome':
            return False  # Déjà diplômé, rien à faire
        
        from apps.gestion_notes.models import UniteEnseignement
        import json
        
        # Récupérer les UE manquantes
        if not self.ue_manquantes:
            # Pas d'UE manquantes enregistrées, devrait être diplômé
            self.statut_diplome = 'diplome'
            self.ue_manquantes = '[]'
            self.save()
            return True
        
        ue_codes_manquantes = json.loads(self.ue_manquantes)
        
        if not ue_codes_manquantes:
            # Liste vide, peut passer à diplômé
            self.statut_diplome = 'diplome'
            self.save()
            return True
        
        # Vérifier chaque UE manquante
        ues_toujours_manquantes = []
        
        for ue_code in ue_codes_manquantes:
            try:
                ue = UniteEnseignement.objects.get(code=ue_code)
                if not ue.est_valide_ue(self.etudiant):
                    ues_toujours_manquantes.append(ue_code)
            except UniteEnseignement.DoesNotExist:
                # UE n'existe plus, on l'ignore
                pass
        
        # Mettre à jour
        if not ues_toujours_manquantes:
            # Toutes les UE sont validées !
            self.statut_diplome = 'diplome'
            self.ue_manquantes = '[]'
            self.save()
            return True
        else:
            # Mettre à jour la liste des UE encore manquantes
            self.ue_manquantes = json.dumps(ues_toujours_manquantes)
            self.save()
            return False


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