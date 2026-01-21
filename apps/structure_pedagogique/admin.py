# structure_pedagogique/admin.py
from django.contrib import admin
from .models import Semestre, Matiere


@admin.register(Semestre)
class SemestreAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'ordre')
    ordering = ('ordre',)


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'niveau', 'semestre', 'coefficient', 'credits')
    list_filter = ('niveau', 'semestre')
    search_fields = ('code', 'nom')
    filter_horizontal = ('enseignants',)