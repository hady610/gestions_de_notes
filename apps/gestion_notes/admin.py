# gestion_notes/admin.py
from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'matiere', 'controle', 'examen', 'get_moyenne', 'statut', 'est_admis')
    list_filter = ('statut', 'matiere__niveau', 'matiere__semestre')
    search_fields = ('etudiant__matricule', 'etudiant__nom', 'etudiant__prenom')
    readonly_fields = ('valide_par', 'valide_le', 'created_at', 'updated_at')
    
    def get_moyenne(self, obj):
        return obj.moyenne()
    get_moyenne.short_description = 'Moyenne'
    
    def save_model(self, request, obj, form, change):
        if obj.statut == 'valide' and not obj.valide_par:
            from django.utils import timezone
            obj.valide_par = request.user
            obj.valide_le = timezone.now()
        super().save_model(request, obj, form, change)