"""
MODULE 4 : Structure Pédagogique - URLs
"""
from django.urls import path
from . import views

app_name = 'structure_pedagogique'

urlpatterns = [
    # Semestres
    path('semestres/', views.semestre_list, name='semestre_list'),
    path('semestres/ajouter/', views.semestre_create, name='semestre_create'),
    path('semestres/<int:pk>/modifier/', views.semestre_update, name='semestre_update'),
    path('semestres/<int:pk>/supprimer/', views.semestre_delete, name='semestre_delete'),
    
    # Matières
    path('matieres/', views.matiere_list, name='matiere_list'),
    path('matieres/ajouter/', views.matiere_create, name='matiere_create'),
    path('matieres/<int:pk>/', views.matiere_detail, name='matiere_detail'),
    path('matieres/<int:pk>/modifier/', views.matiere_update, name='matiere_update'),
    path('matieres/<int:pk>/supprimer/', views.matiere_delete, name='matiere_delete'),
]