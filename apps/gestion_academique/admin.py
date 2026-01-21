# gestion_academique/admin.py
from django.contrib import admin
from .models import Departement, Niveau, AnneeAcademique, Etudiant, Enseignant


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'created_at')
    search_fields = ('code', 'nom')


@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'ordre')
    ordering = ('ordre',)


@admin.register(AnneeAcademique)
class AnneeAcademiqueAdmin(admin.ModelAdmin):
    list_display = ('annee', 'date_debut', 'date_fin', 'est_active')
    list_filter = ('est_active',)


@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'niveau', 'departement', 'annee_academique')
    list_filter = ('niveau', 'departement', 'annee_academique', 'sexe')
    search_fields = ('matricule', 'nom', 'prenom', 'email')
    ordering = ('nom', 'prenom')


@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'prenom', 'grade', 'specialite')
    list_filter = ('grade',)
    search_fields = ('code', 'nom', 'prenom', 'email')
    filter_horizontal = ('departements',)