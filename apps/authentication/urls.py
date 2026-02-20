# authentication/urls.py
from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Connexion / Déconnexion
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profil
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # Changer mot de passe
    path('change-password/', views.change_password_view, name='change_password'),
    
    # Réinitialiser mot de passe (oublié)
    path('password-reset/', views.password_reset_view, name='password_reset'),
    
    # Créer comptes
    path('create-etudiant/', views.create_etudiant_account, name='create_etudiant_account'),
    path('create-enseignant/', views.create_enseignant_account, name='create_enseignant_account'),
    
    # Inscription (optionnel - peut être commenté en production)
    path('register/', views.register_view, name='register'),
]
