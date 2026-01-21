# gestion_academique/views.py
"""
MODULE 2 : Gestion Académique - Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Departement, Niveau, AnneeAcademique, Etudiant, Enseignant
from .forms import DepartementForm, NiveauForm, AnneeAcademiqueForm, EtudiantForm, EnseignantForm


# ==================== DÉPARTEMENTS ====================

@login_required
def departement_list(request):
    """Liste des départements"""
    departements = Departement.objects.annotate(
        nb_etudiants=Count('etudiants')
    ).order_by('nom')
    
    # Recherche
    search = request.GET.get('search', '')
    if search:
        departements = departements.filter(
            Q(code__icontains=search) | Q(nom__icontains=search)
        )
    
    context = {
        'departements': departements,
        'search': search,
        'total': departements.count(),
    }
    return render(request, 'gestion_academique/departements/list.html', context)


@login_required
def departement_create(request):
    """Créer un département"""
    if request.method == 'POST':
        form = DepartementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Département créé avec succès !')
            return redirect('gestion_academique:departement_list')
    else:
        form = DepartementForm()
    
    context = {'form': form}
    return render(request, 'gestion_academique/departements/form.html', context)


@login_required
def departement_update(request, pk):
    """Modifier un département"""
    departement = get_object_or_404(Departement, pk=pk)
    
    if request.method == 'POST':
        form = DepartementForm(request.POST, instance=departement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Département modifié avec succès !')
            return redirect('gestion_academique:departement_list')
    else:
        form = DepartementForm(instance=departement)
    
    context = {'form': form, 'departement': departement}
    return render(request, 'gestion_academique/departements/form.html', context)


@login_required
def departement_delete(request, pk):
    """Supprimer un département"""
    departement = get_object_or_404(Departement, pk=pk)
    
    if request.method == 'POST':
        departement.delete()
        messages.success(request, 'Département supprimé avec succès !')
        return redirect('gestion_academique:departement_list')
    
    context = {'departement': departement}
    return render(request, 'gestion_academique/departements/delete.html', context)


# ==================== NIVEAUX ====================

@login_required
def niveau_list(request):
    """Liste des niveaux"""
    niveaux = Niveau.objects.annotate(
        nb_etudiants=Count('etudiants')
    ).order_by('ordre')
    
    context = {
        'niveaux': niveaux,
        'total': niveaux.count(),
    }
    return render(request, 'gestion_academique/niveaux/list.html', context)


@login_required
def niveau_create(request):
    """Créer un niveau"""
    if request.method == 'POST':
        form = NiveauForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Niveau créé avec succès !')
            return redirect('gestion_academique:niveau_list')
    else:
        form = NiveauForm()
    
    context = {'form': form}
    return render(request, 'gestion_academique/niveaux/form.html', context)


@login_required
def niveau_update(request, pk):
    """Modifier un niveau"""
    niveau = get_object_or_404(Niveau, pk=pk)
    
    if request.method == 'POST':
        form = NiveauForm(request.POST, instance=niveau)
        if form.is_valid():
            form.save()
            messages.success(request, 'Niveau modifié avec succès !')
            return redirect('gestion_academique:niveau_list')
    else:
        form = NiveauForm(instance=niveau)
    
    context = {'form': form, 'niveau': niveau}
    return render(request, 'gestion_academique/niveaux/form.html', context)


@login_required
def niveau_delete(request, pk):
    """Supprimer un niveau"""
    niveau = get_object_or_404(Niveau, pk=pk)
    
    if request.method == 'POST':
        niveau.delete()
        messages.success(request, 'Niveau supprimé avec succès !')
        return redirect('gestion_academique:niveau_list')
    
    context = {'niveau': niveau}
    return render(request, 'gestion_academique/niveaux/delete.html', context)


# ==================== ANNÉES ACADÉMIQUES ====================

@login_required
def annee_list(request):
    """Liste des années académiques"""
    annees = AnneeAcademique.objects.annotate(
        nb_etudiants=Count('etudiants')
    ).order_by('-date_debut')
    
    context = {
        'annees': annees,
        'total': annees.count(),
    }
    return render(request, 'gestion_academique/annees/list.html', context)


@login_required
def annee_create(request):
    """Créer une année académique"""
    if request.method == 'POST':
        form = AnneeAcademiqueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Année académique créée avec succès !')
            return redirect('gestion_academique:annee_list')
    else:
        form = AnneeAcademiqueForm()
    
    context = {'form': form}
    return render(request, 'gestion_academique/annees/form.html', context)


@login_required
def annee_update(request, pk):
    """Modifier une année académique"""
    annee = get_object_or_404(AnneeAcademique, pk=pk)
    
    if request.method == 'POST':
        form = AnneeAcademiqueForm(request.POST, instance=annee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Année académique modifiée avec succès !')
            return redirect('gestion_academique:annee_list')
    else:
        form = AnneeAcademiqueForm(instance=annee)
    
    context = {'form': form, 'annee': annee}
    return render(request, 'gestion_academique/annees/form.html', context)


@login_required
def annee_delete(request, pk):
    """Supprimer une année académique"""
    annee = get_object_or_404(AnneeAcademique, pk=pk)
    
    if request.method == 'POST':
        annee.delete()
        messages.success(request, 'Année académique supprimée avec succès !')
        return redirect('gestion_academique:annee_list')
    
    context = {'annee': annee}
    return render(request, 'gestion_academique/annees/delete.html', context)


# ==================== ÉTUDIANTS ====================

@login_required
def etudiant_list(request):
    """Liste des étudiants"""
    etudiants = Etudiant.objects.select_related(
        'departement', 'niveau', 'annee_academique'
    ).order_by('nom', 'prenom')
    
    # Filtres
    search = request.GET.get('search', '')
    departement = request.GET.get('departement', '')
    niveau = request.GET.get('niveau', '')
    annee = request.GET.get('annee', '')
    
    if search:
        etudiants = etudiants.filter(
            Q(matricule__icontains=search) |
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(email__icontains=search)
        )
    
    if departement:
        etudiants = etudiants.filter(departement_id=departement)
    
    if niveau:
        etudiants = etudiants.filter(niveau_id=niveau)
    
    if annee:
        etudiants = etudiants.filter(annee_academique_id=annee)
    
    # Statistiques
    total = etudiants.count()
    ntic_count = etudiants.filter(departement__code='NTIC').count()
    dl_count = etudiants.filter(departement__code='DL').count()
    
    context = {
        'etudiants': etudiants,
        'total': total,
        'ntic_count': ntic_count,
        'dl_count': dl_count,
        'search': search,
        'departements': Departement.objects.all(),
        'niveaux': Niveau.objects.all(),
        'annees': AnneeAcademique.objects.all(),
    }
    return render(request, 'gestion_academique/etudiants/list.html', context)


@login_required
def etudiant_create(request):
    """Créer un étudiant"""
    if request.method == 'POST':
        form = EtudiantForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Étudiant créé avec succès !')
            return redirect('gestion_academique:etudiant_list')
    else:
        form = EtudiantForm()
    
    context = {'form': form}
    return render(request, 'gestion_academique/etudiants/form.html', context)


@login_required
def etudiant_detail(request, pk):
    """Détails d'un étudiant"""
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    context = {'etudiant': etudiant}
    return render(request, 'gestion_academique/etudiants/detail.html', context)


@login_required
def etudiant_update(request, pk):
    """Modifier un étudiant"""
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    if request.method == 'POST':
        form = EtudiantForm(request.POST, request.FILES, instance=etudiant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Étudiant modifié avec succès !')
            return redirect('gestion_academique:etudiant_detail', pk=pk)
    else:
        form = EtudiantForm(instance=etudiant)
    
    context = {'form': form, 'etudiant': etudiant}
    return render(request, 'gestion_academique/etudiants/form.html', context)


@login_required
def etudiant_delete(request, pk):
    """Supprimer un étudiant"""
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    if request.method == 'POST':
        etudiant.delete()
        messages.success(request, 'Étudiant supprimé avec succès !')
        return redirect('gestion_academique:etudiant_list')
    
    context = {'etudiant': etudiant}
    return render(request, 'gestion_academique/etudiants/delete.html', context)

# ==================== ENSEIGNANTS ====================

@login_required
def enseignant_list(request):
    """Liste des enseignants"""
    enseignants = Enseignant.objects.prefetch_related('departements').order_by('nom', 'prenom')
    
    # Recherche
    search = request.GET.get('search', '')
    if search:
        enseignants = enseignants.filter(
            Q(code__icontains=search) |
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(email__icontains=search)
        )
    
    context = {
        'enseignants': enseignants,
        'total': enseignants.count(),
        'search': search,
    }
    return render(request, 'gestion_academique/enseignants/list.html', context)


@login_required
def enseignant_create(request):
    """Créer un enseignant"""
    if request.method == 'POST':
        form = EnseignantForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enseignant créé avec succès !')
            return redirect('gestion_academique:enseignant_list')
    else:
        form = EnseignantForm()
    
    context = {'form': form}
    return render(request, 'gestion_academique/enseignants/form.html', context)


@login_required
def enseignant_detail(request, pk):
    """Détails d'un enseignant"""
    enseignant = get_object_or_404(Enseignant, pk=pk)
    
    context = {'enseignant': enseignant}
    return render(request, 'gestion_academique/enseignants/detail.html', context)


@login_required
def enseignant_update(request, pk):
    """Modifier un enseignant"""
    enseignant = get_object_or_404(Enseignant, pk=pk)
    
    if request.method == 'POST':
        form = EnseignantForm(request.POST, request.FILES, instance=enseignant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enseignant modifié avec succès !')
            return redirect('gestion_academique:enseignant_detail', pk=pk)
    else:
        form = EnseignantForm(instance=enseignant)
    
    context = {'form': form, 'enseignant': enseignant}
    return render(request, 'gestion_academique/enseignants/form.html', context)


@login_required
def enseignant_delete(request, pk):
    """Supprimer un enseignant"""
    enseignant = get_object_or_404(Enseignant, pk=pk)
    
    if request.method == 'POST':
        enseignant.delete()
        messages.success(request, 'Enseignant supprimé avec succès !')
        return redirect('gestion_academique:enseignant_list')
    
    context = {'enseignant': enseignant}
    return render(request, 'gestion_academique/enseignants/delete.html', context)