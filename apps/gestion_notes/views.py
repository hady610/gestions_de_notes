# gestion_notes/views.py - CORRIGÉ AVEC FILTRE ANNÉE
"""
MODULE 3 : Gestion des Notes - Views (avec permissions par rôle)
CORRECTION : Ajout du filtre par année académique pour les rattrapages
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Note, UniteEnseignement
from .forms import NoteForm, UniteEnseignementForm
from apps.gestion_academique.models import Etudiant, Enseignant, AnneeAcademique
from apps.structure_pedagogique.models import Matiere, Semestre


# ============================================================
# UNITÉS D'ENSEIGNEMENT (Admin + Directeur)
# ============================================================

@login_required
def ue_list(request):
    """Liste des UE - Admin + Directeur peuvent voir et gérer"""
    if not (request.user.profile.is_admin() or request.user.profile.is_chef_departement()):
        messages.error(request, "Vous n'avez pas la permission d'accéder aux UE !")
        return redirect('home')

    ues = UniteEnseignement.objects.select_related('semestre').prefetch_related('matieres')

    if request.user.profile.is_chef_departement():
        ues = ues.filter(matieres__departements=request.user.profile.departement).distinct()

    semestre_id = request.GET.get('semestre', '')
    if semestre_id:
        ues = ues.filter(semestre_id=semestre_id)

    context = {
        'ues': ues,
        'semestres': Semestre.objects.all(),
        'semestre_selectionne': semestre_id,
    }
    return render(request, 'gestion_notes/ue/list.html', context)


@login_required
def ue_create(request):
    """Créer une UE - Admin + Directeur"""
    if not (request.user.profile.is_admin() or request.user.profile.is_chef_departement()):
        messages.error(request, "Vous n'avez pas la permission de créer des UE !")
        return redirect('home')

    if request.method == 'POST':
        form = UniteEnseignementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "UE créée avec succès !")
            return redirect('gestion_notes:ue_list')
    else:
        form = UniteEnseignementForm()

    context = {'form': form}
    return render(request, 'gestion_notes/ue/form.html', context)


@login_required
def ue_update(request, pk):
    """Modifier une UE - Admin + Directeur"""
    if not (request.user.profile.is_admin() or request.user.profile.is_chef_departement()):
        messages.error(request, "Vous n'avez pas la permission de modifier des UE !")
        return redirect('home')

    ue = get_object_or_404(UniteEnseignement, pk=pk)

    if request.method == 'POST':
        form = UniteEnseignementForm(request.POST, instance=ue)
        if form.is_valid():
            form.save()
            messages.success(request, "UE modifiée avec succès !")
            return redirect('gestion_notes:ue_list')
    else:
        form = UniteEnseignementForm(instance=ue)

    context = {'form': form, 'ue': ue}
    return render(request, 'gestion_notes/ue/form.html', context)


@login_required
def ue_delete(request, pk):
    """Supprimer une UE - Admin + Directeur"""
    if not (request.user.profile.is_admin() or request.user.profile.is_chef_departement()):
        messages.error(request, "Vous n'avez pas la permission de supprimer des UE !")
        return redirect('home')

    ue = get_object_or_404(UniteEnseignement, pk=pk)

    if request.method == 'POST':
        try:
            ue.delete()
            messages.success(request, 'UE supprimée avec succès !')
            return redirect('gestion_notes:ue_list')
        except Exception as e:
            messages.error(request, f"❌ Impossible de supprimer l'UE '{ue.nom}' ! "
                          f"Elle est utilisée dans des calculs de moyennes ou bulletins.")
            return redirect('gestion_notes:ue_list')

    context = {'ue': ue}
    return render(request, 'gestion_notes/ue/delete.html', context)


# ============================================================
# SAISIE DES NOTES (ENSEIGNANT) - AVEC FILTRE ANNÉE
# ============================================================

@login_required
def saisie_notes(request):
    """
    Page principale saisie notes pour l'enseignant
    NOUVELLE LOGIQUE :
    - Année active : Tous les étudiants du niveau (nouvelles notes)
    - Année précédente : Seulement les étudiants avec notes NON VALIDÉES (rattrapages)
    """
    if not request.user.profile.is_enseignant():
        messages.error(request, "Vous n'avez pas la permission !")
        return redirect('home')

    enseignant = request.user.profile.enseignant
    matieres = Matiere.objects.filter(enseignants=enseignant)
    
    # Récupérer toutes les années académiques
    annees = AnneeAcademique.objects.all().order_by('-est_active', '-date_debut')
    
    # Année sélectionnée (par défaut : année active)
    annee_id = request.GET.get('annee', '')
    if annee_id:
        annee_selectionnee = get_object_or_404(AnneeAcademique, pk=annee_id)
    else:
        annee_selectionnee = AnneeAcademique.objects.filter(est_active=True).first()
    
    # Filtre par matière
    matiere_id = request.GET.get('matiere', '')
    matiere_selectionnee = None

    if matiere_id and annee_selectionnee:
        matiere_selectionnee = get_object_or_404(Matiere, pk=matiere_id, enseignants=enseignant)
        
        # LOGIQUE DIFFÉRENTE SELON L'ANNÉE
        if annee_selectionnee.est_active:
            # ===== ANNÉE ACTIVE : Tous les étudiants du niveau =====
            etudiants = Etudiant.objects.filter(
                niveau=matiere_selectionnee.niveau,
                departement__in=matiere_selectionnee.departements.all(),
                annee_academique=annee_selectionnee,
                statut='actif'
            ).order_by('nom', 'prenom')
            
        else:
            # ===== ANNÉE PRÉCÉDENTE : Seulement étudiants avec notes NON VALIDÉES =====
            # Récupérer les IDs des étudiants qui ont des notes non validées pour cette matière
            etudiants_avec_notes_non_validees = Note.objects.filter(
                matiere=matiere_selectionnee,
                statut__in=['brouillon', 'invalide']
            ).values_list('etudiant_id', flat=True).distinct()
            
            etudiants = Etudiant.objects.filter(
                id__in=etudiants_avec_notes_non_validees,
                niveau=matiere_selectionnee.niveau,
                departement__in=matiere_selectionnee.departements.all()
            ).order_by('nom', 'prenom')

        # Pour chaque étudiant, récupérer la note existante
        notes_data = []
        for etu in etudiants:
            note, created = Note.objects.get_or_create(
                etudiant=etu,
                matiere=matiere_selectionnee,
                defaults={'enseignant': enseignant, 'statut': 'brouillon'}
            )
            notes_data.append({
                'etudiant': etu,
                'note': note,
                'form': NoteForm(instance=note),
                'peut_modifier': note.peut_modifier(),
            })

        context = {
            'enseignant': enseignant,
            'matieres': matieres,
            'matiere_selectionnee': matiere_selectionnee,
            'notes_data': notes_data,
            'annees': annees,
            'annee_selectionnee': annee_selectionnee,
        }
    else:
        context = {
            'enseignant': enseignant,
            'matieres': matieres,
            'matiere_selectionnee': None,
            'annees': annees,
            'annee_selectionnee': annee_selectionnee,
        }

    return render(request, 'gestion_notes/enseignant/saisie.html', context)


@login_required
def saisie_sauvegarder(request, note_id):
    """Sauvegarder ou soumettre une note individuelle"""
    if not request.user.profile.is_enseignant():
        messages.error(request, "Vous n'avez pas la permission !")
        return redirect('home')

    note = get_object_or_404(Note, pk=note_id)

    if not note.peut_modifier():
        messages.error(request, "Vous ne pouvez pas modifier cette note !")
        return redirect('gestion_notes:saisie_notes')

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save(commit=False)
            
            # NOUVEAU : Vérifier l'action (save ou submit)
            action = request.POST.get('action', 'save')
            
            if action == 'submit':
                note.statut = 'soumis'
                note.date_soumission = timezone.now()
                messages.success(request, f"Note soumise pour {note.etudiant.get_full_name()} !")
            else:
                note.statut = 'brouillon'
                messages.success(request, f"Note sauvegardée pour {note.etudiant.get_full_name()} !")
            
            note.save()

    # Rediriger vers la même page avec le même filtre matière et année
    annee_id = request.GET.get('annee', '')
    url = f"/notes/saisie/?matiere={note.matiere.id}"
    if annee_id:
        url += f"&annee={annee_id}"
    return redirect(url)


@login_required
def saisie_soumettre(request, matiere_id):
    """Soumettre TOUTES les notes d'une matière au chef"""
    if not request.user.profile.is_enseignant():
        messages.error(request, "Vous n'avez pas la permission !")
        return redirect('home')

    enseignant = request.user.profile.enseignant
    matiere = get_object_or_404(Matiere, pk=matiere_id, enseignants=enseignant)

    if request.method == 'POST':
        notes = Note.objects.filter(
            matiere=matiere,
            enseignant=enseignant,
            statut__in=['brouillon', 'invalide']
        )

        if notes.count() == 0:
            messages.error(request, "Aucune note à soumettre !")
            return redirect('gestion_notes:saisie_notes')

        for note in notes:
            note.statut = 'soumis'
            note.date_soumission = timezone.now()
            note.save()

        messages.success(request, f"Notes de {matiere.nom} soumises au Chef de département !")
        return redirect('gestion_notes:saisie_notes')

    context = {'matiere': matiere}
    return render(request, 'gestion_notes/enseignant/soumettre_confirm.html', context)


# ============================================================
# VALIDATION DES NOTES (CHEF DE DÉPARTEMENT) - ANCIEN SYSTÈME
# ============================================================

@login_required
def validation_notes(request):
    """
    Page validation pour le chef de département (ancien système)
    """
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Vous n'avez pas la permission !")
        return redirect('home')

    departement = request.user.profile.departement
    onglet = request.GET.get('onglet', 'soumis')

    if onglet == 'valide':
        notes = Note.objects.filter(
            matiere__departements=departement,
            statut='valide'
        ).select_related('etudiant', 'matiere', 'enseignant').order_by('matiere', 'etudiant__nom')
    else:
        notes = Note.objects.filter(
            matiere__departements=departement,
            statut='soumis'
        ).select_related('etudiant', 'matiere', 'enseignant').order_by('matiere', 'etudiant__nom')

    matiere_id = request.GET.get('matiere', '')
    if matiere_id:
        notes = notes.filter(matiere_id=matiere_id)

    matieres = Matiere.objects.filter(
        departements=departement,
        notes__statut__in=['soumis', 'valide']
    ).distinct()

    context = {
        'notes': notes,
        'matieres': matieres,
        'matiere_selectionnee': matiere_id,
        'departement': departement,
        'onglet': onglet,
    }
    return render(request, 'gestion_notes/chef/validation.html', context)


@login_required
def valider_note(request, note_id):
    """Valider une note"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Vous n'avez pas la permission !")
        return redirect('home')

    note = get_object_or_404(Note, pk=note_id)

    if not note.peut_valider():
        messages.error(request, "Cette note ne peut pas être validée !")
        return redirect('gestion_notes:validation_notes')

    note.statut = 'valide'
    note.date_validation = timezone.now()
    note.save()

    messages.success(request, f"Note validée pour {note.etudiant.get_full_name()} - {note.matiere.nom} !")
    return redirect('gestion_notes:validation_notes')


@login_required
def invalider_note(request, note_id):
    """Invalider une note"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Vous n'avez pas la permission !")
        return redirect('home')

    note = get_object_or_404(Note, pk=note_id)

    if not note.peut_invalider():
        messages.error(request, "Cette note ne peut pas être invalidée !")
        return redirect('gestion_notes:validation_notes')

    note.statut = 'invalide'
    note.save()

    messages.success(request, f"Note invalidée pour {note.etudiant.get_full_name()} - {note.matiere.nom} !")
    return redirect('gestion_notes:validation_notes')


@login_required
def valider_toutes_notes(request, matiere_id):
    """Valider toutes les notes d'une matière"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Vous n'avez pas la permission !")
        return redirect('home')

    departement = request.user.profile.departement
    matiere = get_object_or_404(Matiere, pk=matiere_id, departements=departement)

    notes = Note.objects.filter(matiere=matiere, statut='soumis')
    for note in notes:
        note.statut = 'valide'
        note.date_validation = timezone.now()
        note.save()

    messages.success(request, f"Toutes les notes de {matiere.nom} validées !")
    return redirect('gestion_notes:validation_notes')


# ============================================================
# MES NOTES (ÉTUDIANT)
# ============================================================

@login_required
def mes_notes(request):
    """Page des notes pour l'étudiant"""
    if not request.user.profile.is_etudiant():
        messages.error(request, "Vous n'avez pas la permission !")
        return redirect('home')

    etudiant = request.user.profile.etudiant

    notes = Note.objects.filter(
        etudiant=etudiant,
        statut__in=['soumis', 'valide']
    ).select_related('matiere', 'enseignant').order_by('matiere__semestre__ordre', 'matiere__nom')

    semestres_data = {}
    for note in notes:
        sem = note.matiere.semestre
        if sem not in semestres_data:
            semestres_data[sem] = {
                'notes': [],
                'total_points': 0,
                'total_coef': 0,
            }
        semestres_data[sem]['notes'].append(note)
        semestres_data[sem]['total_points'] += note.moyenne * note.matiere.coefficient
        semestres_data[sem]['total_coef'] += note.matiere.coefficient

    for sem in semestres_data:
        if semestres_data[sem]['total_coef'] > 0:
            semestres_data[sem]['moyenne'] = round(
                semestres_data[sem]['total_points'] / semestres_data[sem]['total_coef'], 2
            )
        else:
            semestres_data[sem]['moyenne'] = 0.0

    ues = UniteEnseignement.objects.filter(
        matieres__notes__etudiant=etudiant,
        matieres__notes__statut__in=['soumis', 'valide']
    ).distinct()

    ues_data = []
    for ue in ues:
        moyenne_ue = ue.calculer_moyenne_ue(etudiant)
        resultat = ue.get_resultat(etudiant)
        ues_data.append({
            'ue': ue,
            'moyenne': moyenne_ue,
            'resultat': resultat,
            'matieres': ue.matieres.all(),
        })

    context = {
        'etudiant': etudiant,
        'notes': notes,
        'semestres_data': semestres_data,
        'ues_data': ues_data,
    }
    return render(request, 'gestion_notes/etudiant/mes_notes.html', context)


# ============================================================
# RELEVÉ DE NOTES (ÉTUDIANT)
# ============================================================

@login_required
def releve_notes(request):
    """Relevé de notes de l'étudiant"""
    if not request.user.profile.is_etudiant():
        messages.error(request, "Vous n'avez pas la permission !")
        return redirect('home')

    etudiant = request.user.profile.etudiant

    notes = Note.objects.filter(
        etudiant=etudiant,
        statut='valide'
    ).select_related('matiere', 'enseignant').order_by('matiere__semestre__ordre', 'matiere__nom')

    ues = UniteEnseignement.objects.filter(
        matieres__notes__etudiant=etudiant,
        matieres__notes__statut='valide'
    ).distinct()

    ues_data = []
    for ue in ues:
        moyenne_ue = ue.calculer_moyenne_ue(etudiant)
        resultat = ue.get_resultat(etudiant)
        ues_data.append({
            'ue': ue,
            'moyenne': moyenne_ue,
            'resultat': resultat,
        })

    context = {
        'etudiant': etudiant,
        'notes': notes,
        'ues_data': ues_data,
    }
    return render(request, 'gestion_notes/etudiant/releve.html', context)