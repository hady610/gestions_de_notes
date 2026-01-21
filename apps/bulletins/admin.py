# bulletins/admin.py
from django.contrib import admin
from .models import Resultat, Bulletin


@admin.register(Resultat)
class ResultatAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'semestre', 'annee_academique', 'moyenne_generale', 
                    'total_credits_obtenus', 'decision', 'genere_le')
    list_filter = ('decision', 'semestre', 'annee_academique')
    search_fields = ('etudiant__matricule', 'etudiant__nom', 'etudiant__prenom')
    readonly_fields = ('genere_le',)


@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display = ('resultat', 'genere_le', 'nombre_telechargements', 'telecharge_le')
    readonly_fields = ('genere_le', 'telecharge_le', 'nombre_telechargements')