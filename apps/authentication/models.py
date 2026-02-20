# authentication/models.py
"""
MODULE 1 : Authentication - Models
Fichier : apps/authentication/models.py
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Profil utilisateur étendu avec 4 rôles
    """
    ROLES = (
        ('admin', 'Direction'),
        ('chef_departement', 'Chef de Département'),
        ('enseignant', 'Enseignant'),
        ('etudiant', 'Étudiant'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=30, choices=ROLES, default='etudiant')
    
    # Champ département pour le Chef de Département ET la Direction
    departement = models.ForeignKey(
        'gestion_academique.Departement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chefs',
        verbose_name="Département géré"
    )
    
    # Pour l'étudiant : lien vers le modèle Etudiant
    etudiant = models.OneToOneField(
        'gestion_academique.Etudiant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profile',
        verbose_name="Profil Étudiant"
    )
    
    # Pour l'enseignant : lien vers le modèle Enseignant
    enseignant = models.ForeignKey(
        'gestion_academique.Enseignant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profile',
        verbose_name="Profil Enseignant"
    )
    
    # Pour Option B : message "changez votre password"
    is_first_login = models.BooleanField(default=True)
    
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        return self.user.get_full_name() or self.user.username
    
    # ===== Méthodes de vérification des rôles =====
    
    def is_admin(self):
        """Vérifie si l'utilisateur est Direction (ex-Doyen)"""
        return self.role == 'admin'
    
    def is_direction(self):
        """
        Vérifie si l'utilisateur est Direction
        (Alias de is_admin pour plus de clarté dans le code)
        """
        return self.role == 'admin'
    
    def is_chef_departement(self):
        """Vérifie si l'utilisateur est Chef de Département"""
        return self.role == 'chef_departement'
    
    def is_enseignant(self):
        """Vérifie si l'utilisateur est Enseignant"""
        return self.role == 'enseignant'
    
    def is_etudiant(self):
        """Vérifie si l'utilisateur est Étudiant"""
        return self.role == 'etudiant'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crée automatiquement un profil quand un User est créé
    Les superusers reçoivent automatiquement le rôle 'admin'
    """
    if created:
        # Si c'est un superuser, lui donner le rôle admin
        if instance.is_superuser:
            Profile.objects.create(user=instance, role='admin')
        else:
            Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarde le profil quand le User est sauvegardé"""
    instance.profile.save()