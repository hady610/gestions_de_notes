"""
MODULE 4 : Structure Pédagogique - Views (avec permissions par rôle)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Semestre, Matiere
from .forms import SemestreForm, MatiereForm


# ==================== SEMESTRES (Admin uniquement) ====================

@login_required
def semestre_list(request):
    """Liste des semestres - Tous peuvent voir"""
    semestres = Semestre.objects.select_related('niveau').annotate(
        nb_matieres=Count('matieres')
    ).order_by('niveau__ordre', 'ordre')
    
    context = {
        'semestres': semestres,
        'total': semestres.count(),
    }
    return render(request, 'structure_pedagogique/semestres/list.html', context)


@login_required
def semestre_create(request):
    """Créer un semestre - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Seul l'Administrateur peut créer des semestres !")
        return redirect('structure_pedagogique:semestre_list')
    
    if request.method == 'POST':
        form = SemestreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Semestre créé avec succès !')
            return redirect('structure_pedagogique:semestre_list')
    else:
        form = SemestreForm()
    
    context = {'form': form}
    return render(request, 'structure_pedagogique/semestres/form.html', context)


@login_required
def semestre_update(request, pk):
    """Modifier un semestre - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Seul l'Administrateur peut modifier des semestres !")
        return redirect('structure_pedagogique:semestre_list')
    
    semestre = get_object_or_404(Semestre, pk=pk)
    
    if request.method == 'POST':
        form = SemestreForm(request.POST, instance=semestre)
        if form.is_valid():
            form.save()
            messages.success(request, 'Semestre modifié avec succès !')
            return redirect('structure_pedagogique:semestre_list')
    else:
        form = SemestreForm(instance=semestre)
    
    context = {'form': form, 'semestre': semestre}
    return render(request, 'structure_pedagogique/semestres/form.html', context)


@login_required
def semestre_delete(request, pk):
    """Supprimer un semestre - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Seul l'Administrateur peut supprimer des semestres !")
        return redirect('structure_pedagogique:semestre_list')
    
    semestre = get_object_or_404(Semestre, pk=pk)
    
    if request.method == 'POST':
        try:
            semestre.delete()  # Remplace "objet" par le nom de ta variable
            messages.success(request, 'Semestre supprimé avec succès !')  # Remplace XXX par "Département", "Niveau", etc.
            return redirect('structure_pedagogique:semestre_list')
        except Exception as e:
            messages.error(request, f"❌ Impossible de supprimer le semestre '{semestre.nom}' ! "
            f"Il contient des matières ou des UE. "
            f"Veuillez d'abord les déplacer ou supprimer.")
            return redirect('structure_pedagogique:semestre_list')
    context = {'semestre': semestre}
    return render(request, 'structure_pedagogique/semestres/delete.html', context)


# ==================== MATIÈRES (Directeur + Admin lecture seule) ====================

@login_required
def matiere_list(request):
    """Liste des matières - Tous peuvent voir"""
    matieres = Matiere.objects.select_related(
        'niveau', 'semestre'
    ).prefetch_related('enseignants', 'departements').order_by('code')
    
    # Si Chef, filtrer par son département
    if request.user.profile.is_chef_departement()  or request.user.profile.is_chef_departement():
        matieres = matieres.filter(departements=request.user.profile.departement)
    
    # Filtres
    search = request.GET.get('search', '')
    departement = request.GET.get('departement', '')
    niveau = request.GET.get('niveau', '')
    semestre = request.GET.get('semestre', '')
    
    if search:
        matieres = matieres.filter(
            Q(code__icontains=search) | Q(nom__icontains=search)
        )
    
    if departement:
        matieres = matieres.filter(departements__id=departement)
    
    if niveau:
        matieres = matieres.filter(niveau_id=niveau)
    
    if semestre:
        matieres = matieres.filter(semestre_id=semestre)
    
    # Pour les filtres
    from apps.gestion_academique.models import Departement, Niveau
    
    context = {
        'matieres': matieres,
        'total': matieres.count(),
        'search': search,
        'departements': Departement.objects.all(),
        'niveaux': Niveau.objects.all(),
        'semestres': Semestre.objects.all(),
    }
    return render(request, 'structure_pedagogique/matieres/list.html', context)


@login_required
def matiere_create(request):
    """Créer une matière - Directeur uniquement"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Seul le Directeur du Programme peut créer des matières !")
        return redirect('structure_pedagogique:matiere_list')
    
    if request.method == 'POST':
        form = MatiereForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matière créée avec succès !')
            return redirect('structure_pedagogique:matiere_list')
    else:
        form = MatiereForm()
    
    context = {'form': form}
    return render(request, 'structure_pedagogique/matieres/form.html', context)


@login_required
def matiere_detail(request, pk):
    """Détails d'une matière - Tous peuvent voir"""
    matiere = get_object_or_404(Matiere, pk=pk)
    
    context = {'matiere': matiere}
    return render(request, 'structure_pedagogique/matieres/detail.html', context)


@login_required
def matiere_update(request, pk):
    """Modifier une matière - Directeur uniquement"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Seul le Directeur du Programme peut modifier des matières !")
        return redirect('structure_pedagogique:matiere_list')
    
    matiere = get_object_or_404(Matiere, pk=pk)
    
    if request.method == 'POST':
        form = MatiereForm(request.POST, instance=matiere)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matière modifiée avec succès !')
            return redirect('structure_pedagogique:matiere_detail', pk=pk)
    else:
        form = MatiereForm(instance=matiere)
    
    context = {'form': form, 'matiere': matiere}
    return render(request, 'structure_pedagogique/matieres/form.html', context)


@login_required
def matiere_delete(request, pk):
    """Supprimer une matière - Directeur uniquement"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Seul le Directeur du Programme peut supprimer des matières !")
        return redirect('structure_pedagogique:matiere_list')
    
    matiere = get_object_or_404(Matiere, pk=pk)
    
    if request.method == 'POST':
        try:
            matiere.delete()  # Remplace "objet" par le nom de ta variable
            messages.success(request, 'Matiere supprimée avec succès !')  # Remplace XXX par "Département", "Niveau", etc.
            return redirect('structure_pedagogique:matiere_list')
        except Exception as e:
            messages.error(request, f"❌ Impossible de supprimer la matière '{matiere.nom}' ! "
            f"Elle possède des notes enregistrées ou fait partie d'une UE. "
            f"Veuillez d'abord supprimer les notes et retirer la matière des UE.")
            return redirect('structure_pedagogique:matiere_list')
    
    context = {'matiere': matiere}
    return render(request, 'structure_pedagogique/matieres/delete.html', context)