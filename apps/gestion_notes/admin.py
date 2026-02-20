# gestion_notes/admin.py
"""
MODULE 3 : Gestion des Notes - Admin
"""
from django.contrib import admin
from .models import Note, UniteEnseignement


@admin.register(UniteEnseignement)
class UniteEnseignementAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'semestre', 'get_nb_matieres']
    list_filter = ['semestre']
    search_fields = ['code', 'nom']
    filter_horizontal = ['matieres']
    
    def get_nb_matieres(self, obj):
        return obj.matieres.count()
    get_nb_matieres.short_description = 'Nb Matières'


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['etudiant', 'matiere', 'note1', 'note2', 'note3', 'moyenne', 'statut', 'date_creation']
    list_filter = ['statut', 'matiere', 'matiere__semestre']
    search_fields = ['etudiant__nom', 'etudiant__prenom', 'matiere__nom']
    readonly_fields = ['moyenne', 'date_creation', 'date_modification', 'date_soumission', 'date_validation']
    
    fieldsets = (
        ('Étudiant et Matière', {
            'fields': ('etudiant', 'matiere', 'enseignant')
        }),
        ('Notes (sur 10)', {
            'fields': ('note1', 'note2', 'note3', 'moyenne')
        }),
        ('Workflow', {
            'fields': ('statut', 'date_creation', 'date_modification', 'date_soumission', 'date_validation')
        }),
    )