"""
MODULE 2 : Gestion Académique - URLs
"""
from django.urls import path
from . import views

app_name = 'gestion_academique'

urlpatterns = [
    # Départements
    path('departements/', views.departement_list, name='departement_list'),
    path('departements/ajouter/', views.departement_create, name='departement_create'),
    path('departements/<int:pk>/modifier/', views.departement_update, name='departement_update'),
    path('departements/<int:pk>/supprimer/', views.departement_delete, name='departement_delete'),
    
    # Niveaux
    path('niveaux/', views.niveau_list, name='niveau_list'),
    path('niveaux/ajouter/', views.niveau_create, name='niveau_create'),
    path('niveaux/<int:pk>/modifier/', views.niveau_update, name='niveau_update'),
    path('niveaux/<int:pk>/supprimer/', views.niveau_delete, name='niveau_delete'),
    
    # Années Académiques
    path('annees/', views.annee_list, name='annee_list'),
    path('annees/ajouter/', views.annee_create, name='annee_create'),
    path('annees/<int:pk>/modifier/', views.annee_update, name='annee_update'),
    path('annees/<int:pk>/supprimer/', views.annee_delete, name='annee_delete'),
    
    # Étudiants
    path('etudiants/', views.etudiant_list, name='etudiant_list'),
    path('etudiants/ajouter/', views.etudiant_create, name='etudiant_create'),
    path('etudiants/<int:pk>/', views.etudiant_detail, name='etudiant_detail'),
    path('etudiants/<int:pk>/modifier/', views.etudiant_update, name='etudiant_update'),
    path('etudiants/<int:pk>/supprimer/', views.etudiant_delete, name='etudiant_delete'),
    
    # Enseignants
    path('enseignants/', views.enseignant_list, name='enseignant_list'),
    path('enseignants/ajouter/', views.enseignant_create, name='enseignant_create'),
    path('enseignants/<int:pk>/', views.enseignant_detail, name='enseignant_detail'),
    path('enseignants/<int:pk>/modifier/', views.enseignant_update, name='enseignant_update'),
    path('enseignants/<int:pk>/supprimer/', views.enseignant_delete, name='enseignant_delete'),
]