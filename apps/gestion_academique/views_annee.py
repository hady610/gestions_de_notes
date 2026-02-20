# gestion_academique/views_annee.py
"""
Vues pour la gestion des années académiques, passage d'année et archivage
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime

from .models import AnneeAcademique, Etudiant, EtudiantArchive, Departement
from .services import PassageAnneeService, ArchivageService
from .forms import AnneeAcademiqueForm


# ==================== ANNÉES ACADÉMIQUES ====================

@login_required
def annee_list(request):
    """Liste des années académiques - Admin et Direction"""
    if not (request.user.profile.is_admin() or request.user.profile.is_direction()):
        messages.error(request, "Accès refusé !")
        return redirect('home')
    
    annees = AnneeAcademique.objects.all().order_by('-date_debut')
    
    context = {
        'annees': annees,
        'total': annees.count(),
    }
    return render(request, 'gestion_academique/annees/list.html', context)


@login_required
def annee_create(request):
    """
    Créer une nouvelle année académique
    Format automatique: YYYY-YYYY+1 basé sur la date de création
    """
    if not (request.user.profile.is_admin() or request.user.profile.is_direction()):
        messages.error(request, "Accès refusé !")
        return redirect('home')
    
    if request.method == 'POST':
        form = AnneeAcademiqueForm(request.POST)
        if form.is_valid():
            annee = form.save(commit=False)
            
            # Générer automatiquement le nom de l'année
            annee.annee = AnneeAcademique.generer_nom_annee(annee.date_debut)
            
            # Vérifier qu'une année avec ce nom n'existe pas déjà
            if AnneeAcademique.objects.filter(annee=annee.annee).exists():
                messages.error(request, f"Une année {annee.annee} existe déjà !")
                return render(request, 'gestion_academique/annees/form.html', {'form': form})
            
            annee.save()
            
            messages.success(request, f'Année académique {annee.annee} créée avec succès !')
            messages.info(request, 
                'Pour effectuer le passage automatique des étudiants vers cette année, '
                'utilisez la fonction "Passage d\'année".')
            
            return redirect('gestion_academique:annee_list')
    else:
        form = AnneeAcademiqueForm()
    
    context = {
        'form': form,
        'exemple_format': 'Ex: Si date de début = 1er sept 2025 → Année = 2025-2026'
    }
    return render(request, 'gestion_academique/annees/form.html', context)


@login_required
def annee_update(request, pk):
    """Modifier une année académique"""
    if not (request.user.profile.is_admin() or request.user.profile.is_direction()):
        messages.error(request, "Accès refusé !")
        return redirect('home')
    
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
    if not request.user.profile.is_admin():
        messages.error(request, "Seul l'admin peut supprimer des années !")
        return redirect('gestion_academique:annee_list')
    
    annee = get_object_or_404(AnneeAcademique, pk=pk)
    
    # Vérifier qu'il n'y a pas d'étudiants dans cette année
    nb_etudiants = Etudiant.objects.filter(annee_academique=annee).count()
    if nb_etudiants > 0:
        messages.error(request, 
            f"Impossible de supprimer l'année {annee.annee} ! "
            f"Elle contient {nb_etudiants} étudiant(s).")
        return redirect('gestion_academique:annee_list')
    
    if request.method == 'POST':
        annee.delete()
        messages.success(request, 'Année académique supprimée avec succès !')
        return redirect('gestion_academique:annee_list')
    
    context = {'annee': annee}
    return render(request, 'gestion_academique/annees/delete.html', context)


# ==================== PASSAGE D'ANNÉE ====================

@login_required
def passage_annee_form(request):
    """
    Formulaire pour lancer le passage automatique d'année
    RÈGLE: Tous les étudiants passent automatiquement
    """
    if not (request.user.profile.is_admin() or request.user.profile.is_direction()):
        messages.error(request, "Accès refusé !")
        return redirect('home')
    
    # Récupérer l'année active (ancienne) et les années candidates (nouvelles)
    try:
        annee_active = AnneeAcademique.objects.get(est_active=True)
    except AnneeAcademique.DoesNotExist:
        messages.error(request, "Aucune année académique active trouvée !")
        return redirect('gestion_academique:annee_list')
    
    # Années candidates : non actives et pas encore utilisées pour un passage
    annees_candidates = AnneeAcademique.objects.filter(
        est_active=False,
        date_debut__gt=annee_active.date_debut
    ).order_by('date_debut')
    
    if not annees_candidates.exists():
        messages.warning(request, 
            "Aucune nouvelle année académique disponible ! "
            "Veuillez d'abord créer la prochaine année académique.")
        return redirect('gestion_academique:annee_create')
    
    # Statistiques sur l'année actuelle
    stats_annee_actuelle = {
        'l1': Etudiant.objects.filter(
            annee_academique=annee_active, 
            niveau__code='L1',
            statut='actif'
        ).count(),
        'l2': Etudiant.objects.filter(
            annee_academique=annee_active, 
            niveau__code='L2',
            statut='actif'
        ).count(),
        'l3': Etudiant.objects.filter(
            annee_academique=annee_active, 
            niveau__code='L3',
            statut='actif'
        ).count(),
    }
    stats_annee_actuelle['total'] = sum(stats_annee_actuelle.values())
    
    context = {
        'annee_active': annee_active,
        'annees_candidates': annees_candidates,
        'stats': stats_annee_actuelle,
    }
    return render(request, 'gestion_academique/passage/form.html', context)


@login_required
def passage_annee_executer(request):
    """
    Exécute le passage automatique d'année
    """
    if not (request.user.profile.is_admin() or request.user.profile.is_direction()):
        messages.error(request, "Accès refusé !")
        return redirect('home')
    
    if request.method != 'POST':
        return redirect('gestion_academique:passage_annee_form')
    
    nouvelle_annee_id = request.POST.get('nouvelle_annee_id')
    
    try:
        ancienne_annee = AnneeAcademique.objects.get(est_active=True)
        nouvelle_annee = AnneeAcademique.objects.get(pk=nouvelle_annee_id)
    except AnneeAcademique.DoesNotExist:
        messages.error(request, "Année académique introuvable !")
        return redirect('gestion_academique:passage_annee_form')
    
    # Vérifier que le passage n'a pas déjà été fait
    if ancienne_annee.passage_effectue:
        messages.warning(request, 
            f"Le passage de l'année {ancienne_annee.annee} a déjà été effectué !")
        return redirect('gestion_academique:annee_list')
    
    # Exécuter le passage
    stats = PassageAnneeService.passage_automatique_annee(ancienne_annee, nouvelle_annee)
    
    # Afficher les résultats
    if stats['erreurs']:
        messages.warning(request, 
            f"Passage effectué avec {len(stats['erreurs'])} erreur(s).")
        for erreur in stats['erreurs'][:5]:  # Limiter à 5 erreurs affichées
            messages.error(request, f"Erreur: {erreur}")
    else:
        messages.success(request, 
            f"✅ Passage d'année réussi vers {nouvelle_annee.annee} !")
    
    messages.info(request, 
        f"L1→L2: {stats['l1_vers_l2']} | "
        f"L2→L3: {stats['l2_vers_l3']} | "
        f"L3 archivés: {stats['l3_archives']} "
        f"(Diplômés: {stats['l3_diplomes']}, Non diplômés: {stats['l3_non_diplomes']})")
    
    return redirect('gestion_academique:annee_list')


# ==================== ARCHIVES (DIPLÔMÉS ET NON-DIPLÔMÉS) ====================

@login_required
def archives_list(request):
    """
    Liste des étudiants archivés (diplômés et non-diplômés)
    
    PERMISSIONS:
    - Direction: voit TOUS les départements
    - Chef de département: voit uniquement SON département
    """
    if not (request.user.profile.is_direction() or request.user.profile.is_chef_departement()):
        messages.error(request, "Accès refusé !")
        return redirect('home')
    
    # Filtrer selon le rôle
    archives = EtudiantArchive.objects.select_related(
        'etudiant', 'departement', 'annee_sortie'
    ).order_by('-date_archivage')
    
    if request.user.profile.is_chef_departement():
        # Chef : uniquement son département
        archives = archives.filter(departement=request.user.profile.departement)
    
    # Filtres
    departement_id = request.GET.get('departement', '')
    annee_id = request.GET.get('annee_sortie', '')
    statut = request.GET.get('statut', '')
    search = request.GET.get('search', '')
    
    if departement_id:
        archives = archives.filter(departement_id=departement_id)
    
    if annee_id:
        archives = archives.filter(annee_sortie_id=annee_id)
    
    if statut:
        archives = archives.filter(statut_diplome=statut)
    
    if search:
        archives = archives.filter(
            Q(etudiant__matricule__icontains=search) |
            Q(etudiant__nom__icontains=search) |
            Q(etudiant__prenom__icontains=search)
        )
    
    # Statistiques
    stats = {
        'total': archives.count(),
        'diplomes': archives.filter(statut_diplome='diplome').count(),
        'non_diplomes': archives.filter(statut_diplome='non_diplome').count(),
    }
    
    # Données pour les filtres
    departements = Departement.objects.all()
    if request.user.profile.is_chef_departement():
        departements = departements.filter(pk=request.user.profile.departement.pk)
    
    annees = AnneeAcademique.objects.filter(
        sortants__isnull=False
    ).distinct().order_by('-date_debut')
    
    context = {
        'archives': archives,
        'stats': stats,
        'departements': departements,
        'annees': annees,
        'filters': {
            'departement': departement_id,
            'annee': annee_id,
            'statut': statut,
            'search': search,
        }
    }
    return render(request, 'gestion_academique/archives/list.html', context)


@login_required
def archive_detail(request, pk):
    """Détails d'un étudiant archivé"""
    if not (request.user.profile.is_direction() or request.user.profile.is_chef_departement()):
        messages.error(request, "Accès refusé !")
        return redirect('home')
    
    archive = get_object_or_404(EtudiantArchive, pk=pk)
    
    # Vérifier les permissions
    if request.user.profile.is_chef_departement():
        if archive.departement != request.user.profile.departement:
            messages.error(request, "Vous ne pouvez voir que les archives de votre département !")
            return redirect('gestion_academique:archives_list')
    
    # Récupérer les UE manquantes si non diplômé
    ues_manquantes = []
    if archive.statut_diplome == 'non_diplome' and archive.ue_manquantes:
        import json
        from apps.gestion_notes.models import UniteEnseignement
        
        ue_codes = json.loads(archive.ue_manquantes)
        for code in ue_codes:
            try:
                ue = UniteEnseignement.objects.get(code=code)
                ues_manquantes.append({
                    'ue': ue,
                    'est_valide': ue.est_valide_ue(archive.etudiant),
                    'moyenne': ue.calculer_moyenne_ue(archive.etudiant)
                })
            except UniteEnseignement.DoesNotExist:
                pass
    
    context = {
        'archive': archive,
        'ues_manquantes': ues_manquantes,
    }
    return render(request, 'gestion_academique/archives/detail.html', context)


@login_required
def archives_verifier_maj(request):
    """
    Vérifie et met à jour automatiquement le statut des étudiants archivés
    Passage de "non_diplome" à "diplome" si toutes les UE sont validées
    """
    if not (request.user.profile.is_admin() or request.user.profile.is_direction() or request.user.profile.is_chef_departement()):
        messages.error(request, "Accès refusé !")
        return redirect('home')
    
    if request.method != 'POST':
        return redirect('gestion_academique:archives_list')
    
    resultat = ArchivageService.verifier_maj_archives_auto()
    
    if resultat['passages_diplome'] > 0:
        messages.success(request, 
            f"✅ {resultat['passages_diplome']} étudiant(s) "
            f"sont maintenant marqués comme diplômés !")
    else:
        messages.info(request, 
            "Aucun changement de statut détecté.")
    
    messages.info(request, 
        f"{resultat['verifies']} archive(s) vérifiée(s).")
    
    return redirect('gestion_academique:archives_list')