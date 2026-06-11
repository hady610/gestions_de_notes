# gestion_academique/urls.py - VERSION CORRIGÉE
"""
URLs pour la gestion académique étendue
Inclut: années académiques, passage d'année, passage manuel, archives
"""
from django.urls import path
from . import views
from . import views_import
from . import views_annee  # Nouvelles vues

app_name = 'gestion_academique'

urlpatterns = [
    # ==================== DÉPARTEMENTS ====================
    path('departements/', views.departement_list, name='departement_list'),
    path('departements/creer/', views.departement_create, name='departement_create'),
    path('departements/<int:pk>/modifier/', views.departement_update, name='departement_update'),
    path('departements/<int:pk>/supprimer/', views.departement_delete, name='departement_delete'),
    
    # ==================== NIVEAUX ====================
    path('niveaux/', views.niveau_list, name='niveau_list'),
    path('niveaux/creer/', views.niveau_create, name='niveau_create'),
    path('niveaux/<int:pk>/modifier/', views.niveau_update, name='niveau_update'),
    path('niveaux/<int:pk>/supprimer/', views.niveau_delete, name='niveau_delete'),
    
    # ==================== ANNÉES ACADÉMIQUES ====================
    path('annees/', views_annee.annee_list, name='annee_list'),
    path('annees/creer/', views_annee.annee_create, name='annee_create'),
    path('annees/<int:pk>/modifier/', views_annee.annee_update, name='annee_update'),
    path('annees/<int:pk>/supprimer/', views_annee.annee_delete, name='annee_delete'),
    
    # ==================== PASSAGE D'ANNÉE AUTOMATIQUE ====================
    path('passage-annee/', views_annee.passage_annee_form, name='passage_annee_form'),
    path('passage-annee/executer/', views_annee.passage_annee_executer, name='passage_annee_executer'),
    
    # ⭐⭐⭐ PASSAGE MANUEL (NOUVEAU) ⭐⭐⭐
    path('passage-manuel/', views_annee.passage_manuel_liste, name='passage_manuel_liste'),
    path('passage-manuel/<int:etudiant_id>/executer/', views_annee.passage_manuel_executer, name='passage_manuel_executer'),
    path('passage-manuel/<int:etudiant_id>/annuler/', views_annee.passage_manuel_annuler, name='passage_manuel_annuler'),
    path('passage-manuel/historique/', views_annee.passage_manuel_historique, name='passage_manuel_historique'),
    # ==================== ARCHIVES ====================
    path('archives/', views_annee.archives_list, name='archives_list'),
    path('archives/<int:pk>/', views_annee.archive_detail, name='archive_detail'),
    path('archives/verifier-maj/', views_annee.archives_verifier_maj, name='archives_verifier_maj'),
    
    # ==================== ÉTUDIANTS ====================
    path('etudiants/', views.etudiant_list, name='etudiant_list'),
    path('etudiants/creer/', views.etudiant_create, name='etudiant_create'),
    path('etudiants/<int:pk>/', views.etudiant_detail, name='etudiant_detail'),
    path('etudiants/<int:pk>/modifier/', views.etudiant_update, name='etudiant_update'),
    path('etudiants/<int:pk>/supprimer/', views.etudiant_delete, name='etudiant_delete'),
    
    # ==================== ENSEIGNANTS ====================
    path('enseignants/', views.enseignant_list, name='enseignant_list'),
    path('enseignants/creer/', views.enseignant_create, name='enseignant_create'),
    path('enseignants/<int:pk>/', views.enseignant_detail, name='enseignant_detail'),
    path('enseignants/<int:pk>/modifier/', views.enseignant_update, name='enseignant_update'),
    path('enseignants/<int:pk>/supprimer/', views.enseignant_delete, name='enseignant_delete'),

    # ==================== IMPORT ====================
    path('import/etudiants/', views_import.import_etudiants_page, name='import_etudiants'),
    path('import/modele-excel/', views_import.telecharger_modele_excel, name='telecharger_modele_excel'),
]