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

from .models import AnneeAcademique, Etudiant, EtudiantArchive, Departement, Niveau
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
    MODIFIÉ : Affiche maintenant les statistiques de redoublement
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
    
    # Afficher les résultats - VERSION AMÉLIORÉE
    if stats['erreurs']:
        messages.warning(request, 
            f"Passage effectué avec {len(stats['erreurs'])} erreur(s).")
        for erreur in stats['erreurs'][:5]:  # Limiter à 5 erreurs affichées
            messages.error(request, f"Erreur: {erreur}")
    else:
        messages.success(request, 
            f"✅ Passage d'année réussi vers {nouvelle_annee.annee} !")
    
    # ⭐ NOUVEAU : Messages détaillés avec redoublements
    messages.info(request, 
        f"📊 Passages : L1→L2: {stats['l1_vers_l2']} | L2→L3: {stats['l2_vers_l3']}")
    
    # Afficher les passages manuels s'il y en a
    total_manuels = stats['l1_vers_l2_manuel'] + stats['l2_vers_l3_manuel']
    if total_manuels > 0:
        messages.success(request, 
            f"🔓 Passages manuels : {total_manuels} (L1→L2: {stats['l1_vers_l2_manuel']}, L2→L3: {stats['l2_vers_l3_manuel']})")
    
    # ⭐ NOUVEAU : Afficher les redoublements
    total_redoublants = stats['l1_redouble'] + stats['l2_redouble']
    if total_redoublants > 0:
        messages.warning(request, 
            f"⚠️ Redoublements : {total_redoublants} étudiants (L1: {stats['l1_redouble']}, L2: {stats['l2_redouble']})")
        messages.info(request, 
            f"💡 Vous pouvez gérer les passages manuels depuis le menu 'Passage Manuel'")
    
    # Afficher les archives L3
    messages.info(request, 
        f"📁 L3 archivés: {stats['l3_archives']} "
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


# ==================== PASSAGE MANUEL ====================

@login_required
def passage_manuel_liste(request):
    """
    Liste des étudiants éligibles au passage manuel
    Affiche les étudiants qui ont 4 dettes ou plus et qui pourraient être passés manuellement
    
    PERMISSION: Direction uniquement
    """
    if not request.user.profile.is_direction():
        messages.error(request, "Accès refusé ! Réservé à la direction.")
        return redirect('home')
    
    # Récupérer l'année active
    try:
        annee_active = AnneeAcademique.objects.get(est_active=True)
    except AnneeAcademique.DoesNotExist:
        messages.error(request, "Aucune année académique active !")
        return redirect('gestion_academique:annee_list')
    
    # Récupérer tous les étudiants actifs (L1 et L2 uniquement)
    etudiants = Etudiant.objects.filter(
        annee_academique=annee_active,
        statut='actif',
        niveau__ordre__lt=3  # Uniquement L1 et L2
    ).select_related('niveau', 'departement')
    
    # Calculer les dettes pour chaque étudiant
    etudiants_avec_dettes = []
    
    for etudiant in etudiants:
        nb_dettes = etudiant.compter_ues_non_validees()
        peut_passer, raison = etudiant.peut_passer_niveau_superieur()
        
        etudiants_avec_dettes.append({
            'etudiant': etudiant,
            'nb_dettes': nb_dettes,
            'peut_passer': peut_passer,
            'raison': raison,
            'doit_redoubler': nb_dettes >= 4 and not etudiant.passage_manuel
        })
    
    # Filtres
    departement_id = request.GET.get('departement', '')
    niveau_id = request.GET.get('niveau', '')
    afficher_tous = request.GET.get('tous', '') == 'oui'
    
    if departement_id:
        etudiants_avec_dettes = [
            e for e in etudiants_avec_dettes 
            if str(e['etudiant'].departement.id) == departement_id
        ]
    
    if niveau_id:
        etudiants_avec_dettes = [
            e for e in etudiants_avec_dettes 
            if str(e['etudiant'].niveau.id) == niveau_id
        ]
    
    # Par défaut, afficher seulement ceux qui doivent redoubler (4+ dettes)
    if not afficher_tous:
        etudiants_avec_dettes = [
            e for e in etudiants_avec_dettes 
            if e['doit_redoubler']
        ]
    
    # Statistiques
    stats = {
        'total': len(etudiants_avec_dettes),
        'passages_manuels_existants': Etudiant.objects.filter(
            annee_academique=annee_active,
            passage_manuel=True
        ).count()
    }
    
    # Données pour filtres
    departements = Departement.objects.all()
    niveaux = Niveau.objects.filter(ordre__lt=3)  # L1 et L2 uniquement
    
    context = {
        'etudiants_avec_dettes': etudiants_avec_dettes,
        'annee_active': annee_active,
        'stats': stats,
        'departements': departements,
        'niveaux': niveaux,
        'filters': {
            'departement': departement_id,
            'niveau': niveau_id,
            'tous': afficher_tous
        }
    }
    return render(request, 'gestion_academique/passage/manuel_liste.html', context)


@login_required
def passage_manuel_executer(request, etudiant_id):
    """
    Exécute le passage manuel d'un étudiant spécifique
    
    PERMISSION: Direction uniquement
    """
    if not request.user.profile.is_direction():
        messages.error(request, "Accès refusé ! Réservé à la direction.")
        return redirect('home')
    
    if request.method != 'POST':
        return redirect('gestion_academique:passage_manuel_liste')
    
    etudiant = get_object_or_404(Etudiant, pk=etudiant_id)
    justification = request.POST.get('justification', '').strip()
    
    # Vérifier que la justification est fournie
    if not justification:
        messages.error(request, "La justification est obligatoire pour un passage manuel !")
        return redirect('gestion_academique:passage_manuel_liste')
    
    # Effectuer le passage
    resultat = PassageAnneeService.passage_manuel_etudiant(
        etudiant=etudiant,
        user_direction=request.user,
        justification=justification
    )
    
    if resultat['success']:
        messages.success(request, resultat['message'])
        messages.info(request, 
            f"Détails : {resultat['details']['nb_dettes']} dettes | "
            f"{resultat['details']['ancien_niveau']} → {resultat['details']['nouveau_niveau']}")
    else:
        messages.error(request, resultat['message'])
    
    return redirect('gestion_academique:passage_manuel_liste')


@login_required
def passage_manuel_annuler(request, etudiant_id):
    """
    Annule le passage manuel d'un étudiant
    (le remet au niveau précédent)
    
    PERMISSION: Direction uniquement
    """
    if not request.user.profile.is_direction():
        messages.error(request, "Accès refusé ! Réservé à la direction.")
        return redirect('home')
    
    if request.method != 'POST':
        return redirect('gestion_academique:passage_manuel_liste')
    
    etudiant = get_object_or_404(Etudiant, pk=etudiant_id)
    
    # Vérifier que c'est bien un passage manuel
    if not etudiant.passage_manuel:
        messages.error(request, "Cet étudiant n'a pas fait l'objet d'un passage manuel !")
        return redirect('gestion_academique:passage_manuel_liste')
    
    try:
        # Récupérer le niveau précédent
        niveau_precedent = Niveau.objects.get(ordre=etudiant.niveau.ordre - 1)
        
        ancien_niveau = etudiant.niveau.code
        
        # Annuler le passage
        etudiant.niveau = niveau_precedent
        etudiant.passage_manuel = False
        etudiant.passage_manuel_par = None
        etudiant.passage_manuel_date = None
        etudiant.passage_manuel_justification = ""
        etudiant.save()
        
        messages.success(request, 
            f"✅ Passage manuel annulé : {ancien_niveau} → {niveau_precedent.code}")
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l'annulation : {str(e)}")
    
    return redirect('gestion_academique:passage_manuel_liste')


# AJOUTER CETTE VUE dans apps/gestion_academique/views_annee.py
# (après la fonction passage_manuel_annuler)

@login_required
def passage_manuel_historique(request):
    """
    Historique de tous les passages manuels effectués
    
    PERMISSION: Direction uniquement
    """
    if not request.user.profile.is_direction():
        messages.error(request, "Accès refusé ! Réservé à la direction.")
        return redirect('home')
    
    # Récupérer tous les étudiants avec passage manuel
    etudiants = Etudiant.objects.filter(
        passage_manuel=True
    ).select_related(
        'niveau', 'departement', 'annee_academique', 'passage_manuel_par'
    ).order_by('-passage_manuel_date')
    
    # Filtres
    departement_id = request.GET.get('departement', '')
    annee_id = request.GET.get('annee', '')
    niveau_id = request.GET.get('niveau', '')
    search = request.GET.get('search', '')
    
    if departement_id:
        etudiants = etudiants.filter(departement_id=departement_id)
    
    if annee_id:
        etudiants = etudiants.filter(annee_academique_id=annee_id)
    
    if niveau_id:
        etudiants = etudiants.filter(niveau_id=niveau_id)
    
    if search:
        etudiants = etudiants.filter(
            Q(matricule__icontains=search) |
            Q(nom__icontains=search) |
            Q(prenom__icontains=search)
        )
    
    # Statistiques
    stats = {
        'total': etudiants.count(),
        'par_niveau': etudiants.values('niveau__code').annotate(
            total=Count('id')
        ).order_by('niveau__code'),
        'par_departement': etudiants.values('departement__code').annotate(
            total=Count('id')
        ).order_by('departement__code'),
    }
    
    # Données pour filtres
    departements = Departement.objects.all()
    annees = AnneeAcademique.objects.all().order_by('-date_debut')
    niveaux = Niveau.objects.all().order_by('ordre')
    
    context = {
        'etudiants': etudiants,
        'stats': stats,
        'departements': departements,
        'annees': annees,
        'niveaux': niveaux,
        'filters': {
            'departement': departement_id,
            'annee': annee_id,
            'niveau': niveau_id,
            'search': search,
        }
    }
    return render(request, 'gestion_academique/passage/historique.html', context)