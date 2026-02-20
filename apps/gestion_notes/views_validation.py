# gestion_notes/views_validation.py - CORRIGÉ AVEC FILTRE ANNÉE
"""
Vues étendues pour la validation des notes avec filtres avancés
CORRECTION : Ajout du filtre par année académique pour les rattrapages
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from .models import Note
from .forms import NoteForm
from apps.gestion_academique.models import Etudiant, AnneeAcademique
from apps.structure_pedagogique.models import Matiere


# ============================================================
# VALIDATION DES NOTES (CHEF DÉPARTEMENT) - AVEC FILTRE ANNÉE
# ============================================================================

@login_required
def validation_notes_list(request):
    """
    Liste des notes à valider avec filtres étendus
    NOUVELLE LOGIQUE :
    - Année active : Notes à valider de la nouvelle année
    - Année précédente : Notes à valider (rattrapages)
    """
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Accès réservé aux chefs de département")
        return redirect('home')
    
    departement = request.user.profile.departement
    
    # Récupérer toutes les années académiques
    annees = AnneeAcademique.objects.all().order_by('-est_active', '-date_debut')
    
    # Année sélectionnée (par défaut : année active)
    annee_id = request.GET.get('annee', '')
    if annee_id:
        annee_selectionnee = get_object_or_404(AnneeAcademique, pk=annee_id)
    else:
        annee_selectionnee = AnneeAcademique.objects.filter(est_active=True).first()
    
    # Filtres
    niveau_code = request.GET.get('niveau', '')
    statut = request.GET.get('statut', '')
    matricule = request.GET.get('matricule', '')
    
    # Base query
    notes = Note.objects.filter(
        matiere__departements=departement
    ).select_related(
        'etudiant', 'matiere', 'enseignant', 'etudiant__niveau'
    ).order_by('-date_soumission', 'matiere__nom', 'etudiant__nom')
    
    # LOGIQUE DIFFÉRENTE SELON L'ANNÉE
    if annee_selectionnee:
        if annee_selectionnee.est_active:
            # ===== ANNÉE ACTIVE : Notes des étudiants de l'année active =====
            notes = notes.filter(etudiant__annee_academique=annee_selectionnee)
        else:
            # ===== ANNÉE PRÉCÉDENTE : Seulement les notes NON VALIDÉES (rattrapages) =====
            notes = notes.filter(
                etudiant__annee_academique=annee_selectionnee,
                statut__in=['brouillon', 'soumis', 'invalide']  # Exclut les validées
            )
    
    # Filtres additionnels
    if niveau_code:
        notes = notes.filter(etudiant__niveau__code=niveau_code)
    
    if statut:
        notes = notes.filter(statut=statut)
    
    if matricule:
        notes = notes.filter(etudiant__matricule__icontains=matricule)
    
    # Statistiques
    stats = {
        'total_etudiants': notes.values('etudiant').distinct().count(),
        'soumis': notes.filter(statut='soumis').count(),
        'valide': notes.filter(statut='valide').count(),
        'invalide': notes.filter(statut='invalide').count(),
        'total_notes': notes.count(),
    }
    
    context = {
        'notes': notes,
        'stats': stats,
        'departement': departement,
        'annees': annees,
        'annee_selectionnee': annee_selectionnee,
        'filters': {
            'niveau': niveau_code,
            'statut': statut,
            'matricule': matricule,
        }
    }
    
    return render(request, 'gestion_notes/validation/list.html', context)


@login_required
def validation_notes_valider(request, note_id):
    """Valider une note individuelle"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Accès réservé aux chefs de département")
        return redirect('home')
    
    note = get_object_or_404(Note, pk=note_id)
    
    # Vérifier que la note appartient au département du chef
    if note.matiere.departements.filter(pk=request.user.profile.departement.pk).exists():
        if note.statut == 'soumis':
            note.statut = 'valide'
            note.date_validation = timezone.now()
            note.save()
            messages.success(request, f"Note validée : {note.etudiant.get_full_name()} - {note.matiere.nom}")
        else:
            messages.warning(request, "Cette note n'est pas en attente de validation")
    else:
        messages.error(request, "Cette note n'appartient pas à votre département")
    
    return redirect('gestion_notes:validation_notes_list')


@login_required
def validation_notes_invalider(request, note_id):
    """Invalider une note (renvoyer à l'enseignant)"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Accès réservé aux chefs de département")
        return redirect('home')
    
    note = get_object_or_404(Note, pk=note_id)
    
    if note.matiere.departements.filter(pk=request.user.profile.departement.pk).exists():
        if note.statut in ['soumis', 'valide']:
            note.statut = 'invalide'
            note.save()
            messages.success(request, f"Note invalidée : {note.etudiant.get_full_name()} - {note.matiere.nom}")
        else:
            messages.warning(request, "Cette note ne peut pas être invalidée")
    else:
        messages.error(request, "Cette note n'appartient pas à votre département")
    
    return redirect('gestion_notes:validation_notes_list')


@login_required
def validation_notes_valider_lot(request):
    """Valider plusieurs notes en lot"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Accès réservé aux chefs de département")
        return redirect('home')
    
    if request.method == 'POST':
        note_ids = request.POST.getlist('note_ids')
        
        if note_ids:
            notes = Note.objects.filter(
                pk__in=note_ids,
                matiere__departements=request.user.profile.departement,
                statut='soumis'
            )
            
            count = 0
            for note in notes:
                note.statut = 'valide'
                note.date_validation = timezone.now()
                note.save()
                count += 1
            
            messages.success(request, f"{count} note(s) validée(s) avec succès")
        else:
            messages.warning(request, "Aucune note sélectionnée")
    
    return redirect('gestion_notes:validation_notes_list')


# ============================================================
# SAISIE DES NOTES (ENSEIGNANT) - NOUVEAU SYSTÈME
# ============================================================

@login_required
def enseignant_notes_list(request):
    """
    Liste des notes de l'enseignant avec filtres
    NOUVELLE LOGIQUE :
    - Année active : Toutes les notes
    - Année précédente : Seulement les notes NON VALIDÉES
    """
    if not request.user.profile.is_enseignant():
        messages.error(request, "Accès réservé aux enseignants")
        return redirect('home')
    
    enseignant = request.user.profile.enseignant
    
    # Récupérer toutes les années académiques
    annees = AnneeAcademique.objects.all().order_by('-est_active', '-date_debut')
    
    # Année sélectionnée (par défaut : année active)
    annee_id = request.GET.get('annee', '')
    if annee_id:
        annee_selectionnee = get_object_or_404(AnneeAcademique, pk=annee_id)
    else:
        annee_selectionnee = AnneeAcademique.objects.filter(est_active=True).first()
    
    # Filtres
    matiere_id = request.GET.get('matiere', '')
    
    # Base query
    notes = Note.objects.filter(
        enseignant=enseignant
    ).select_related('etudiant', 'matiere', 'etudiant__niveau')
    
    # LOGIQUE DIFFÉRENTE SELON L'ANNÉE
    if annee_selectionnee:
        if annee_selectionnee.est_active:
            # ===== ANNÉE ACTIVE : Toutes les notes =====
            notes = notes.filter(etudiant__annee_academique=annee_selectionnee)
        else:
            # ===== ANNÉE PRÉCÉDENTE : Seulement notes NON VALIDÉES =====
            notes = notes.filter(
                etudiant__annee_academique=annee_selectionnee,
                statut__in=['brouillon', 'invalide']
            )
    
    # Filtre par matière
    if matiere_id:
        matiere_selectionnee = get_object_or_404(Matiere, pk=matiere_id)
        notes = notes.filter(matiere=matiere_selectionnee)
    else:
        matiere_selectionnee = None
    
    # Statistiques
    stats = {
        'total': notes.count(),
        'brouillon': notes.filter(statut='brouillon').count(),
        'soumis': notes.filter(statut='soumis').count(),
        'valide': notes.filter(statut='valide').count(),
        'invalide': notes.filter(statut='invalide').count(),
    }
    
    # Matières de l'enseignant
    matieres = Matiere.objects.filter(enseignants=enseignant)
    
    # Étudiants en dette (si matière sélectionnée et année précédente)
    etudiants_dette = None
    if matiere_selectionnee and annee_selectionnee and not annee_selectionnee.est_active:
        # Étudiants avec notes non validées
        etudiants_avec_notes = notes.filter(matiere=matiere_selectionnee).values_list('etudiant_id', flat=True)
        etudiants_dette = {
            'total': len(etudiants_avec_notes),
            'avec_notes': list(etudiants_avec_notes),
            'sans_notes': []
        }
    
    context = {
        'notes': notes,
        'stats': stats,
        'matieres': matieres,
        'matiere_selectionnee': matiere_selectionnee,
        'annees': annees,
        'annee_selectionnee': annee_selectionnee,
        'etudiants_dette': etudiants_dette,
    }
    
    return render(request, 'gestion_notes/enseignant/list.html', context)


@login_required
def enseignant_note_saisir(request, etudiant_id, matiere_id):
    """Formulaire de saisie/modification d'une note"""
    if not request.user.profile.is_enseignant():
        messages.error(request, "Accès réservé aux enseignants")
        return redirect('home')
    
    enseignant = request.user.profile.enseignant
    etudiant = get_object_or_404(Etudiant, pk=etudiant_id)
    matiere = get_object_or_404(Matiere, pk=matiere_id, enseignants=enseignant)
    
    # Récupérer ou créer la note
    note, created = Note.objects.get_or_create(
        etudiant=etudiant,
        matiere=matiere,
        defaults={'enseignant': enseignant, 'statut': 'brouillon'}
    )
    
    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        
        # Récupérer les notes
        note1 = request.POST.get('note1')
        note2 = request.POST.get('note2')
        note3 = request.POST.get('note3')
        
        if note1 and note2 and note3:
            note.note1 = float(note1)
            note.note2 = float(note2)
            note.note3 = float(note3)
            
            if action == 'submit':
                note.statut = 'soumis'
                note.date_soumission = timezone.now()
                messages.success(request, f"Note soumise pour validation : {etudiant.get_full_name()}")
            else:
                note.statut = 'brouillon'
                messages.success(request, f"Note sauvegardée en brouillon : {etudiant.get_full_name()}")
            
            note.save()
            return redirect('gestion_notes:enseignant_notes_list')
        else:
            messages.error(request, "Veuillez remplir les 3 notes")
    
    context = {
        'etudiant': etudiant,
        'matiere': matiere,
        'note': note,
        'created': created,
    }
    
    return render(request, 'gestion_notes/enseignant/saisir.html', context)