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
    
    # Inscription (optionnel - peut être commenté en production)
    path('register/', views.register_view, name='register'),
]
