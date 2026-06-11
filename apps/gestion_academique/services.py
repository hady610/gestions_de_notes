# gestion_academique/services.py - VERSION MODIFIÉE
"""
Services pour la gestion du passage d'année et de l'archivage
MODIFIÉ : Ajout règle des 4 dettes max + passage manuel
"""
from django.db import transaction
from django.utils import timezone
from apps.gestion_academique.models import (
    Etudiant, AnneeAcademique, Niveau, EtudiantArchive
)
from apps.gestion_notes.models import UniteEnseignement, Note
import json


class PassageAnneeService:
    """
    Service pour gérer le passage automatique d'une année à l'autre
    NOUVELLE RÈGLE: Maximum 3 dettes (UE non validées) pour passer
    """
    
    @staticmethod
    def passage_automatique_annee(ancienne_annee, nouvelle_annee):
        """
        Effectue le passage des étudiants vers l'année suivante
        avec vérification de la règle des 4 dettes max
        
        RÈGLE:
        - 0 à 3 UE non validées → Passe au niveau supérieur
        - 4 UE non validées ou plus → Redouble
        - Passage manuel → Passe automatiquement (ignore dettes)
        
        Args:
            ancienne_annee: AnneeAcademique qui se termine
            nouvelle_annee: AnneeAcademique qui commence
            
        Returns:
            dict: Statistiques détaillées du passage
        """
        stats = {
            # Passages normaux
            'l1_vers_l2': 0,
            'l2_vers_l3': 0,
            
            # Redoublements (nouveauté)
            'l1_redouble': 0,
            'l2_redouble': 0,
            
            # Passages manuels
            'l1_vers_l2_manuel': 0,
            'l2_vers_l3_manuel': 0,
            
            # L3 archivés
            'l3_archives': 0,
            'l3_diplomes': 0,
            'l3_non_diplomes': 0,
            
            # Détails des redoublements
            'redoublants_detail': [],
            
            # Erreurs
            'erreurs': []
        }
        
        try:
            with transaction.atomic():
                # Récupérer tous les étudiants actifs de l'ancienne année
                etudiants = Etudiant.objects.filter(
                    annee_academique=ancienne_annee,
                    statut='actif'
                ).select_related('niveau', 'departement')
                
                for etudiant in etudiants:
                    try:
                        # Déterminer le niveau suivant
                        niveau_actuel_ordre = etudiant.niveau.ordre
                        
                        if niveau_actuel_ordre < 3:
                            # L1 ou L2 → Vérifier les dettes
                            
                            # Vérifier si l'étudiant peut passer
                            peut_passer, raison = etudiant.peut_passer_niveau_superieur()
                            
                            if peut_passer:
                                # ✅ PASSAGE AU NIVEAU SUPÉRIEUR
                                niveau_suivant = Niveau.objects.get(ordre=niveau_actuel_ordre + 1)
                                
                                etudiant.niveau = niveau_suivant
                                etudiant.annee_academique = nouvelle_annee
                                etudiant.save()
                                
                                # Comptabiliser
                                if niveau_actuel_ordre == 1:
                                    if etudiant.passage_manuel:
                                        stats['l1_vers_l2_manuel'] += 1
                                    else:
                                        stats['l1_vers_l2'] += 1
                                else:
                                    if etudiant.passage_manuel:
                                        stats['l2_vers_l3_manuel'] += 1
                                    else:
                                        stats['l2_vers_l3'] += 1
                            
                            else:
                                # ❌ REDOUBLEMENT
                                # L'étudiant reste au même niveau mais change d'année
                                
                                etudiant.annee_academique = nouvelle_annee
                                # Le niveau reste le même (pas de changement)
                                etudiant.save()
                                
                                # Comptabiliser
                                if niveau_actuel_ordre == 1:
                                    stats['l1_redouble'] += 1
                                else:
                                    stats['l2_redouble'] += 1
                                
                                # Enregistrer les détails
                                nb_dettes = etudiant.compter_ues_non_validees()
                                stats['redoublants_detail'].append({
                                    'matricule': etudiant.matricule,
                                    'nom': etudiant.get_full_name(),
                                    'niveau': etudiant.niveau.code,
                                    'nb_dettes': nb_dettes,
                                    'raison': raison
                                })
                        
                        else:
                            # L3 → Archivage
                            resultat_archivage = ArchivageService.archiver_etudiant_sortant(
                                etudiant, nouvelle_annee
                            )
                            
                            stats['l3_archives'] += 1
                            if resultat_archivage['statut'] == 'diplome':
                                stats['l3_diplomes'] += 1
                            else:
                                stats['l3_non_diplomes'] += 1
                    
                    except Exception as e:
                        stats['erreurs'].append({
                            'etudiant': etudiant.get_full_name(),
                            'erreur': str(e)
                        })
                
                # Marquer l'ancienne année comme ayant effectué le passage
                ancienne_annee.passage_effectue = True
                ancienne_annee.date_passage = timezone.now()
                ancienne_annee.est_active = False
                ancienne_annee.save()
                
                # Activer la nouvelle année
                nouvelle_annee.est_active = True
                nouvelle_annee.save()
        
        except Exception as e:
            stats['erreurs'].append({
                'general': str(e)
            })
        
        return stats
    
    
    @staticmethod
    def passage_manuel_etudiant(etudiant, user_direction, justification=""):
        """
        Force le passage manuel d'un étudiant au niveau supérieur
        (ignore la règle des 4 dettes)
        
        PERMISSION: Réservé à la direction uniquement
        
        Args:
            etudiant: Etudiant à faire passer
            user_direction: User de la direction qui effectue le passage
            justification: Raison du passage manuel
            
        Returns:
            dict: Résultat de l'opération
        """
        try:
            # Vérifier que l'étudiant n'est pas déjà au dernier niveau
            if etudiant.niveau.ordre >= 3:
                return {
                    'success': False,
                    'message': "Impossible : l'étudiant est déjà en L3"
                }
            
            # Récupérer l'année active
            try:
                annee_active = AnneeAcademique.objects.get(est_active=True)
            except AnneeAcademique.DoesNotExist:
                return {
                    'success': False,
                    'message': "Aucune année académique active"
                }
            
            # Vérifier que l'étudiant est dans l'année active
            if etudiant.annee_academique != annee_active:
                return {
                    'success': False,
                    'message': f"L'étudiant n'est pas dans l'année active ({etudiant.annee_academique.annee})"
                }
            
            # Récupérer le niveau suivant
            niveau_suivant = Niveau.objects.get(ordre=etudiant.niveau.ordre + 1)
            
            # Compter les dettes avant passage
            nb_dettes = etudiant.compter_ues_non_validees()
            
            # Effectuer le passage
            ancien_niveau = etudiant.niveau.code
            
            etudiant.niveau = niveau_suivant
            etudiant.passage_manuel = True
            etudiant.passage_manuel_par = user_direction
            etudiant.passage_manuel_date = timezone.now()
            etudiant.passage_manuel_justification = justification or f"Passage manuel malgré {nb_dettes} dettes"
            etudiant.save()
            
            return {
                'success': True,
                'message': f"✅ Passage manuel effectué : {ancien_niveau} → {niveau_suivant.code}",
                'details': {
                    'ancien_niveau': ancien_niveau,
                    'nouveau_niveau': niveau_suivant.code,
                    'nb_dettes': nb_dettes,
                    'date': etudiant.passage_manuel_date,
                    'par': user_direction.get_full_name()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Erreur lors du passage manuel : {str(e)}"
            }


class ArchivageService:
    """
    Service pour gérer l'archivage des étudiants sortants (fin L3)
    """
    
    @staticmethod
    def archiver_etudiant_sortant(etudiant, annee_sortie):
        """
        Archive un étudiant sortant de L3
        Détermine automatiquement s'il est diplômé ou non
        
        Args:
            etudiant: Etudiant à archiver
            annee_sortie: AnneeAcademique de sortie
            
        Returns:
            dict: Informations sur l'archivage
        """
        # Vérifier si l'étudiant a validé TOUTES les UE de L1 à L3
        ues_non_validees = ArchivageService.get_ues_non_validees(etudiant)
        
        if not ues_non_validees:
            # Étudiant diplômé
            statut_diplome = 'diplome'
            ue_manquantes_json = '[]'
        else:
            # Étudiant non diplômé
            statut_diplome = 'non_diplome'
            ue_codes = [ue.code for ue in ues_non_validees]
            ue_manquantes_json = json.dumps(ue_codes)
        
        # Créer ou mettre à jour l'archive
        archive, created = EtudiantArchive.objects.update_or_create(
            etudiant=etudiant,
            annee_sortie=annee_sortie,
            defaults={
                'departement': etudiant.departement,
                'statut_diplome': statut_diplome,
                'ue_manquantes': ue_manquantes_json,
            }
        )
        
        # Mettre à jour le statut de l'étudiant
        if statut_diplome == 'diplome':
            etudiant.statut = 'diplome'
        else:
            etudiant.statut = 'archive'
        etudiant.save()
        
        return {
            'statut': statut_diplome,
            'ues_manquantes': len(ues_non_validees),
            'created': created
        }
    
    @staticmethod
    def get_ues_non_validees(etudiant):
        """
        Retourne la liste des UE non validées pour un étudiant
        Vérifie TOUTES les UE de L1 à L3
        
        Args:
            etudiant: Etudiant à vérifier
            
        Returns:
            list: Liste des UniteEnseignement non validées
        """
        # Récupérer toutes les UE du département de l'étudiant
        # pour les niveaux L1, L2, L3 (ordre 1, 2, 3)
        ues = UniteEnseignement.objects.filter(
            semestre__niveau__ordre__lte=3,
            matieres__departements=etudiant.departement
        ).distinct()
        
        ues_non_validees = []
        
        for ue in ues:
            if not ue.est_valide_ue(etudiant):
                ues_non_validees.append(ue)
        
        return ues_non_validees
    
    @staticmethod
    def verifier_maj_archives_auto():
        """
        Vérifie tous les étudiants archivés "non diplômés"
        et met à jour automatiquement leur statut s'ils ont validé leurs UE manquantes
        
        Returns:
            dict: Nombre d'étudiants dont le statut a changé
        """
        archives_non_diplomes = EtudiantArchive.objects.filter(
            statut_diplome='non_diplome'
        )
        
        nb_passages_diplome = 0
        
        for archive in archives_non_diplomes:
            if archive.verifier_et_maj_statut():
                nb_passages_diplome += 1
                # Mettre à jour aussi le statut de l'étudiant
                archive.etudiant.statut = 'diplome'
                archive.etudiant.save()
        
        return {
            'verifies': archives_non_diplomes.count(),
            'passages_diplome': nb_passages_diplome
        }


class GestionNotesService:
    """
    Service pour la gestion des notes et validations avec années antérieures
    """
    
    @staticmethod
    def get_etudiants_pour_validation(departement, annee_academique=None, niveau=None):
        """
        Retourne les étudiants dont les notes sont à valider pour le chef de département
        
        RÈGLE: Lors de la création d'une nouvelle année, les étudiants en dette
        sont automatiquement supprimés de la liste de validation de l'année courante
        
        Args:
            departement: Département du chef
            annee_academique: Année académique (None = année active)
            niveau: Niveau à filtrer (optionnel)
            
        Returns:
            QuerySet: Étudiants actifs avec notes à valider
        """
        if annee_academique is None:
            annee_academique = AnneeAcademique.objects.get(est_active=True)
        
        # Pour l'année courante : uniquement les étudiants actifs
        # Pour les années précédentes : tous les étudiants (y compris archivés)
        annee_active = AnneeAcademique.objects.get(est_active=True)
        
        if annee_academique == annee_active:
            # Année courante : seulement étudiants actifs
            etudiants = Etudiant.objects.filter(
                departement=departement,
                annee_academique=annee_academique,
                statut='actif'
            )
        else:
            # Année précédente : tous les étudiants de cette année
            etudiants = Etudiant.objects.filter(
                departement=departement,
                annee_academique=annee_academique
            )
        
        if niveau:
            etudiants = etudiants.filter(niveau=niveau)
        
        return etudiants
    
    @staticmethod
    def get_etudiants_en_dette_pour_prof(enseignant, matiere, annee_academique):
        """
        Retourne les étudiants en dette pour une matière spécifique
        pour une année académique donnée
        
        Args:
            enseignant: Enseignant
            matiere: Matière
            annee_academique: Année académique
            
        Returns:
            QuerySet: Étudiants ayant des notes non validées pour cette matière/année
        """
        # Récupérer les notes non validées de cette matière pour cette année
        notes_non_validees = Note.objects.filter(
            matiere=matiere,
            enseignant=enseignant,
            etudiant__annee_academique=annee_academique
        ).exclude(
            statut='valide'
        ).select_related('etudiant')
        
        # Récupérer aussi les étudiants qui n'ont pas encore de note
        etudiants_sans_note = Etudiant.objects.filter(
            departement__in=matiere.departements.all(),
            niveau=matiere.niveau,
            annee_academique=annee_academique
        ).exclude(
            notes__matiere=matiere
        )
        
        # Combiner les deux
        etudiants_avec_notes = [note.etudiant for note in notes_non_validees]
        
        return {
            'avec_notes': etudiants_avec_notes,
            'sans_notes': list(etudiants_sans_note),
            'total': len(etudiants_avec_notes) + etudiants_sans_note.count()
        }