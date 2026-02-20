# gestion_notes/urls.py - ÉTENDU
"""
URLs pour la gestion des notes étendue
Inclut: validation avec filtres, saisie par année
"""
from django.urls import path
from . import views
from . import views_validation  # Nouvelles vues

app_name = 'gestion_notes'

urlpatterns = [
    # ==================== UNITÉS D'ENSEIGNEMENT ====================
    path('ue/', views.ue_list, name='ue_list'),
    path('ue/creer/', views.ue_create, name='ue_create'),
    path('ue/<int:pk>/modifier/', views.ue_update, name='ue_update'),
    path('ue/<int:pk>/supprimer/', views.ue_delete, name='ue_delete'),
    
    # ==================== SAISIE DES NOTES (ENSEIGNANT) - ANCIEN SYSTÈME ====================
    path('saisie/', views.saisie_notes, name='saisie_notes'),
    path('saisie/sauvegarder/<int:note_id>/', views.saisie_sauvegarder, name='saisie_sauvegarder'),
    path('saisie/soumettre/<int:matiere_id>/', views.saisie_soumettre, name='saisie_soumettre'),
    
    # ==================== VALIDATION DES NOTES (CHEF DÉPARTEMENT) - ÉTENDU ====================
    path('validation/', views_validation.validation_notes_list, name='validation_notes_list'),
    path('validation/<int:note_id>/valider/', views_validation.validation_notes_valider, name='validation_notes_valider'),
    path('validation/<int:note_id>/invalider/', views_validation.validation_notes_invalider, name='validation_notes_invalider'),
    path('validation/valider-lot/', views_validation.validation_notes_valider_lot, name='validation_notes_valider_lot'),
    
    # ==================== SAISIE DES NOTES (ENSEIGNANT) - NOUVEAU SYSTÈME ====================
    path('enseignant/notes/', views_validation.enseignant_notes_list, name='enseignant_notes_list'),
    path('enseignant/notes/saisir/<int:etudiant_id>/<int:matiere_id>/', 
         views_validation.enseignant_note_saisir, name='enseignant_note_saisir'),
    
    # ==================== CONSULTATION NOTES (ÉTUDIANT) ====================
    path('etudiant/mes-notes/', views.mes_notes, name='etudiant_notes'),
    path('etudiant/releve/', views.releve_notes, name='etudiant_releve'),
]