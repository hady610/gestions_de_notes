# gestion_academique/services.py
"""
Services pour la gestion du passage d'année et de l'archivage
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
    RÈGLE: Tous les étudiants passent automatiquement (pas de redoublement)
    """
    
    @staticmethod
    def passage_automatique_annee(ancienne_annee, nouvelle_annee):
        """
        Effectue le passage automatique de tous les étudiants vers l'année suivante
        
        Args:
            ancienne_annee: AnneeAcademique qui se termine
            nouvelle_annee: AnneeAcademique qui commence
            
        Returns:
            dict: Statistiques du passage (nb étudiants passés, archivés, etc.)
        """
        stats = {
            'l1_vers_l2': 0,
            'l2_vers_l3': 0,
            'l3_archives': 0,
            'l3_diplomes': 0,
            'l3_non_diplomes': 0,
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
                            # L1 → L2 ou L2 → L3
                            niveau_suivant = Niveau.objects.get(ordre=niveau_actuel_ordre + 1)
                            
                            etudiant.niveau = niveau_suivant
                            etudiant.annee_academique = nouvelle_annee
                            etudiant.save()
                            
                            if niveau_actuel_ordre == 1:
                                stats['l1_vers_l2'] += 1
                            else:
                                stats['l2_vers_l3'] += 1
                        
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