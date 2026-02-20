# bulletins/urls.py
# bulletins/urls.py
"""
MODULE 5 : Bulletins - URLs
"""
from django.urls import path
from . import views

app_name = 'bulletins'

urlpatterns = [
    # Liste des étudiants pour génération bulletins
    path('', views.liste_bulletins, name='liste_bulletins'),
    
    # Générer le bulletin PDF pour un étudiant
    path('generer/<int:etudiant_id>/', views.generer_bulletin_pdf, name='generer_bulletin_pdf'),
    path('detail/<int:etudiant_id>/', views.bulletin_detail, name='bulletin_detail'),
]
