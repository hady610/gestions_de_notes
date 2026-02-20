# gestion_academique/views.py
"""
MODULE 2 : Gestion Académique - Views (avec permissions par rôle)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Departement, Niveau, AnneeAcademique, Etudiant, Enseignant
from .forms import DepartementForm, NiveauForm, AnneeAcademiqueForm, EtudiantForm, EnseignantForm


# ==================== DÉPARTEMENTS (Admin uniquement) ====================

@login_required
def departement_list(request):
    """Liste des départements - Tous peuvent voir"""
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
    """Créer un département - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Vous n'avez pas la permission de créer des départements !")
        return redirect('gestion_academique:departement_list')
    
    if request.method == 'POST':
        form = DepartementForm(request.POST)
        if form.is_valid():
            departement = form.save()
            
            # Créer automatiquement un compte Chef de Département
            from django.contrib.auth.models import User
            
            # Générer username : CHEF-<CODE_DEPT> (ex: CHEF-NTIC)
            username_chef = f"CHEF-{departement.code}"
            password_chef = username_chef  # Mot de passe par défaut = username
            
            # Vérifier si le compte n'existe pas déjà
            if not User.objects.filter(username=username_chef).exists():
                # Créer le user
                chef_user = User.objects.create_user(
                    username=username_chef,
                    password=password_chef,
                    first_name=f"Chef {departement.code}",
                    last_name=departement.nom
                )
                
                # Configurer le profil
                chef_user.profile.role = 'chef_departement'
                chef_user.profile.departement = departement
                chef_user.profile.is_first_login = True
                chef_user.profile.save()
                
                messages.success(request, f'Département créé avec succès !')
                messages.info(request, f'✅ Compte Chef créé → Username: {username_chef} | Password: {password_chef}')
            else:
                messages.success(request, 'Département créé avec succès !')
                messages.warning(request, f'⚠️ Un compte avec le username {username_chef} existe déjà.')
            
            return redirect('gestion_academique:departement_list')
    else:
        form = DepartementForm()
    
    context = {'form': form}
    return render(request, 'gestion_academique/departements/form.html', context)


@login_required
def departement_update(request, pk):
    """Modifier un département - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Vous n'avez pas la permission de modifier des départements !")
        return redirect('gestion_academique:departement_list')
    
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
    """Supprimer un département - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Vous n'avez pas la permission de supprimer des départements !")
        return redirect('gestion_academique:departement_list')
    
    departement = get_object_or_404(Departement, pk=pk)
    
    if request.method == 'POST':
        try:
            departement.delete()  # Remplace "objet" par le nom de ta variable
            messages.success(request, 'Departement supprimé avec succès !')  # Remplace XXX par "Département", "Niveau", etc.
            return redirect('gestion_academique:departement_list')
        except Exception as e:
            messages.error(request, f"❌ Impossible de supprimer le département '{departement.nom}' ! "
            f"Il contient des étudiants, enseignants ou matières. "
            f"Veuillez d'abord les déplacer ou supprimer.")
            return redirect('gestion_academique:departement_list')
    
    context = {'departement': departement}
    return render(request, 'gestion_academique/departements/delete.html', context)


# ==================== NIVEAUX (Admin uniquement) ====================

@login_required
def niveau_list(request):
    """Liste des niveaux - Tous peuvent voir"""
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
    """Créer un niveau - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Vous n'avez pas la permission de créer des niveaux !")
        return redirect('gestion_academique:niveau_list')
    
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
    """Modifier un niveau - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Vous n'avez pas la permission de modifier des niveaux !")
        return redirect('gestion_academique:niveau_list')
    
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
    """Supprimer un niveau - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Vous n'avez pas la permission de supprimer des niveaux !")
        return redirect('gestion_academique:niveau_list')
    
    niveau = get_object_or_404(Niveau, pk=pk)
    
    if request.method == 'POST':
        try:
            niveau.delete()  
            messages.success(request, 'Niveau supprimé avec succès !')  # nt", "Niveau", etc.
            return redirect('gestion_academique:niveau_list')
        except Exception as e:
            messages.error(request, f"❌ Impossible de supprimer le niveau '{niveau.nom}' ! "
            f"Il contient des étudiants ou des semestres. "
            f"Veuillez d'abord les déplacer ou supprimer.")
            return redirect('gestion_academique:niveau_list')

    
    context = {'niveau': niveau}
    return render(request, 'gestion_academique/niveaux/delete.html', context)


# ==================== ANNÉES ACADÉMIQUES (Admin uniquement) ====================

@login_required
def annee_list(request):
    """Liste des années académiques - Tous peuvent voir"""
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
    """Créer une année académique - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Vous n'avez pas la permission de créer des années académiques !")
        return redirect('gestion_academique:annee_list')
    
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
    """Modifier une année académique - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Vous n'avez pas la permission de modifier des années académiques !")
        return redirect('gestion_academique:annee_list')
    
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
    """Supprimer une année académique - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Vous n'avez pas la permission de supprimer des années académiques !")
        return redirect('gestion_academique:annee_list')
    
    annee = get_object_or_404(AnneeAcademique, pk=pk)
    
    if request.method == 'POST':
        try:
            annee.delete()  # Remplace "objet" par le nom de ta variable
            messages.success(request, 'Annee supprimée avec succès !')  # Remplace XXX par "Département", "Niveau", etc.
            return redirect('gestion_academique:annee_list')
        except Exception as e:
            messages.error(request, f"❌ Impossible de supprimer l'année '{annee.annee}' ! "
            f"Des étudiants sont encore inscrits pour cette année. "
            f"Veuillez d'abord les réinscrire dans une autre année.")
            return redirect('gestion_academique:annee_list')
    
    context = {'annee': annee}
    return render(request, 'gestion_academique/annees/delete.html', context)


# ==================== ÉTUDIANTS (Chef de département + Admin lecture seule) ====================

@login_required
def etudiant_list(request):
    """Liste des étudiants - Filtrage par département pour Chef"""
    etudiants = Etudiant.objects.select_related(
        'departement', 'niveau', 'annee_academique'
    ).order_by('nom', 'prenom')
    
    # Si Chef de département, filtrer par son département uniquement
    if request.user.profile.is_chef_departement()  or request.user.profile.is_chef_departement():
        etudiants = etudiants.filter(departement=request.user.profile.departement)
    
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
    """Créer un étudiant - Chef de département uniquement"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Seul le Chef de département peut créer des étudiants !")
        return redirect('gestion_academique:etudiant_list')
    
    if request.method == 'POST':
        form = EtudiantForm(request.POST, request.FILES)
        if form.is_valid():
            etudiant = form.save(commit=False)
            # Forcer le département du chef (même si modifié dans le form)
            etudiant.departement = request.user.profile.departement
            etudiant.save()
            
            # Créer automatiquement un compte pour l'étudiant
            from django.contrib.auth.models import User
            
            # Username = Matricule (ex: 001-234-567-890)
            username_etudiant = etudiant.matricule
            password_etudiant = etudiant.matricule  # Mot de passe par défaut = matricule
            
            # Vérifier si le compte n'existe pas déjà
            if not User.objects.filter(username=username_etudiant).exists():
                # Créer le user
                etudiant_user = User.objects.create_user(
                    username=username_etudiant,
                    password=password_etudiant,
                    first_name=etudiant.prenom,
                    last_name=etudiant.nom,
                    email=etudiant.email or ''
                )
                
                # Configurer le profil
                etudiant_user.profile.role = 'etudiant'
                etudiant_user.profile.etudiant = etudiant
                etudiant_user.profile.is_first_login = True
                etudiant_user.profile.save()
                
                messages.success(request, f'Étudiant créé avec succès !')
                messages.info(request, f'✅ Compte créé → Username: {username_etudiant} | Password: {password_etudiant}')
            else:
                messages.success(request, 'Étudiant créé avec succès !')
                messages.warning(request, f'⚠️ Un compte avec le matricule {username_etudiant} existe déjà.')
            
            return redirect('gestion_academique:etudiant_list')
    else:
        form = EtudiantForm(initial={'departement': request.user.profile.departement})
    
    context = {
        'form': form,
        'force_departement': request.user.profile.departement,
    }
    return render(request, 'gestion_academique/etudiants/form.html', context)
@login_required
def etudiant_detail(request, pk):
    """Détails d'un étudiant - Tous peuvent voir"""
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    # Si Chef, vérifier que c'est son département
    if request.user.profile.is_chef_departement():
        if etudiant.departement != request.user.profile.departement:
            messages.error(request, "Vous ne pouvez voir que les étudiants de votre département !")
            return redirect('gestion_academique:etudiant_list')
    
    context = {'etudiant': etudiant}
    return render(request, 'gestion_academique/etudiants/detail.html', context)



@login_required
def etudiant_update(request, pk):
    """Modifier un étudiant - Chef de département uniquement"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Seul le Chef de département peut modifier des étudiants !")
        return redirect('gestion_academique:etudiant_list')
    
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    # Vérifier que c'est son département
    if etudiant.departement != request.user.profile.departement:
        messages.error(request, "Vous ne pouvez modifier que les étudiants de votre département !")
        return redirect('gestion_academique:etudiant_list')
    
    if request.method == 'POST':
        form = EtudiantForm(request.POST, request.FILES, instance=etudiant)
        if form.is_valid():
            etudiant = form.save(commit=False)
            # Forcer le département (ne peut pas être changé)
            etudiant.departement = request.user.profile.departement
            etudiant.save()
            messages.success(request, 'Étudiant modifié avec succès !')
            return redirect('gestion_academique:etudiant_detail', pk=pk)
    else:
        form = EtudiantForm(instance=etudiant)
    
    context = {
        'form': form,
        'etudiant': etudiant,
        'force_departement': request.user.profile.departement,
    }
    return render(request, 'gestion_academique/etudiants/form.html', context)
@login_required
def etudiant_delete(request, pk):
    """Supprimer un étudiant - Chef de département uniquement"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Seul le Chef de département peut supprimer des étudiants !")
        return redirect('gestion_academique:etudiant_list')
    
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    # Vérifier que c'est son département
    if etudiant.departement != request.user.profile.departement:
        messages.error(request, "Vous ne pouvez supprimer que les étudiants de votre département !")
        return redirect('gestion_academique:etudiant_list')
    
    if request.method == 'POST':
        try:
            etudiant.delete()  # Remplace "objet" par le nom de ta variable
            messages.success(request, 'Etudiant supprimé avec succès !')  # Remplace XXX par "Département", "Niveau", etc.
            return redirect('gestion_academique:etudiant_list')
        except Exception as e:
            messages.error(request, f"❌ Impossible de supprimer l'étudiant '{etudiant.get_full_name()}' ! "
            f"Il possède des notes enregistrées. "
            f"Veuillez d'abord supprimer ses notes.")
            return redirect('gestion_academique:etudiant_list')
    
    context = {'etudiant': etudiant}
    return render(request, 'gestion_academique/etudiants/delete.html', context)


# ==================== ENSEIGNANTS (Directeur + Admin lecture seule) ====================

@login_required
def enseignant_list(request):
    """Liste des enseignants - Tous peuvent voir"""
    enseignants = Enseignant.objects.prefetch_related('departements').order_by('nom', 'prenom')
    
    # Si Chef, filtrer par son département
    if request.user.profile.is_chef_departement()  or request.user.profile.is_chef_departement():
        enseignants = enseignants.filter(departements=request.user.profile.departement)
    
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
    """Créer un enseignant - Directeur uniquement"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Seul le Directeur du Programme peut créer des enseignants !")
        return redirect('gestion_academique:enseignant_list')
    
    if request.method == 'POST':
        form = EnseignantForm(request.POST, request.FILES)
        if form.is_valid():
            enseignant = form.save()
            
            # Créer automatiquement un compte pour l'enseignant
            from django.contrib.auth.models import User
            
            # Username = Code (ex: ENS-001)
            username_enseignant = enseignant.code
            password_enseignant = enseignant.code  # Mot de passe par défaut = code
            
            # Vérifier si le compte n'existe pas déjà
            if not User.objects.filter(username=username_enseignant).exists():
                # Créer le user
                enseignant_user = User.objects.create_user(
                    username=username_enseignant,
                    password=password_enseignant,
                    first_name=enseignant.prenom,
                    last_name=enseignant.nom,
                    email=enseignant.email or ''
                )
                
                # Configurer le profil
                enseignant_user.profile.role = 'enseignant'
                enseignant_user.profile.enseignant = enseignant
                enseignant_user.profile.is_first_login = True
                enseignant_user.profile.save()
                
                messages.success(request, f'Enseignant créé avec succès !')
                messages.info(request, f'✅ Compte créé → Username: {username_enseignant} | Password: {password_enseignant}')
            else:
                messages.success(request, 'Enseignant créé avec succès !')
                messages.warning(request, f'⚠️ Un compte avec le code {username_enseignant} existe déjà.')
            
            return redirect('gestion_academique:enseignant_list')
    else:
        form = EnseignantForm()
    
    context = {'form': form}
    return render(request, 'gestion_academique/enseignants/form.html', context)


@login_required
def enseignant_detail(request, pk):
    """Détails d'un enseignant - Tous peuvent voir"""
    enseignant = get_object_or_404(Enseignant, pk=pk)
    
    context = {'enseignant': enseignant}
    return render(request, 'gestion_academique/enseignants/detail.html', context)


@login_required
def enseignant_update(request, pk):
    """Modifier un enseignant - Directeur uniquement"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Seul le Directeur du Programme peut modifier des enseignants !")
        return redirect('gestion_academique:enseignant_list')
    
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
    """Supprimer un enseignant - Directeur uniquement"""
    if not request.user.profile.is_chef_departement():
        messages.error(request, "Seul le Directeur du Programme peut supprimer des enseignants !")
        return redirect('gestion_academique:enseignant_list')
    
    enseignant = get_object_or_404(Enseignant, pk=pk)
    
    if request.method == 'POST':
        try:
            enseignant.delete()  # Remplace "objet" par le nom de ta variable
            messages.success(request, 'Enseignant supprimé avec succès !')  # Remplace XXX par "Département", "Niveau", etc.
            return redirect('gestion_academique:enseignant_list')
        except Exception as e:
            messages.error(request,  f"❌ Impossible de supprimer l'enseignant '{enseignant.get_full_name()}' ! "
            f"Il est assigné à des matières ou a saisi des notes. "
            f"Veuillez d'abord retirer ses assignations.")
            return redirect('gestion_academique:enseignant_list')
    
    context = {'enseignant': enseignant}
    return render(request, 'gestion_academique/enseignants/delete.html', context)