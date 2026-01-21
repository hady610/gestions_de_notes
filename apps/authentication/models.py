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
    Profil utilisateur étendu avec rôle
    """
    ROLES = (
        ('admin', 'Administrateur'),
        ('enseignant', 'Enseignant'),
        ('etudiant', 'Étudiant'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLES, default='etudiant')
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
    
    def is_admin(self):
        """Vérifie si l'utilisateur est administrateur"""
        return self.role == 'admin'
    
    def is_enseignant(self):
        """Vérifie si l'utilisateur est enseignant"""
        return self.role == 'enseignant'
    
    def is_etudiant(self):
        """Vérifie si l'utilisateur est étudiant"""
        return self.role == 'etudiant'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil quand un User est créé"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarde le profil quand le User est sauvegardé"""
    instance.profile.save()
