# bulletins/views.py
# bulletins/views.py
"""
MODULE 5 : Bulletins - Génération PDF des relevés de notes
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from io import BytesIO
from datetime import datetime
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from apps.gestion_academique.models import Etudiant, AnneeAcademique
from apps.gestion_notes.models import Note, UniteEnseignement
from apps.structure_pedagogique.models import Matiere, Semestre


# Mapping Niveau → Semestres
SEMESTRES_PAR_NIVEAU = {
    'L1': ['S1', 'S2'],
    'L2': ['S3', 'S4'],
    'L3': ['S5', 'S6'],
}


@login_required
def liste_bulletins(request):
    """Page de gestion des bulletins - Admin uniquement"""
    if not request.user.profile.is_admin():
        messages.error(request, "Seul l'Administrateur peut générer des bulletins !")
        return redirect('home')
    
    # Liste des étudiants avec filtre
    etudiants = Etudiant.objects.select_related('departement', 'niveau', 'annee_academique').order_by('nom', 'prenom')
    
    # Filtres
    departement_id = request.GET.get('departement', '')
    niveau_code = request.GET.get('niveau', '')
    matricule = request.GET.get('matricule', '').strip()
    
    if departement_id:
        etudiants = etudiants.filter(departement_id=departement_id)
    
    if niveau_code:
        etudiants = etudiants.filter(niveau__code=niveau_code)
    
    # Recherche par matricule
    if matricule:
        etudiants = etudiants.filter(matricule__icontains=matricule)
    
    from apps.gestion_academique.models import Departement, Niveau
    
    context = {
        'etudiants': etudiants,
        'departements': Departement.objects.all(),
        'niveaux': Niveau.objects.all(),
        'matricule_search': matricule,
    }
    return render(request, 'bulletins/liste.html', context)


@login_required
def generer_bulletin_pdf(request, etudiant_id):
    """Générer le bulletin annuel PDF pour un étudiant"""
    
    # Vérification permission
    if not request.user.profile.is_admin():
        return HttpResponseForbidden("Seul l'Administrateur peut générer des bulletins !")
    
    # Récupérer l'étudiant
    etudiant = get_object_or_404(Etudiant, pk=etudiant_id)
    
    # Déterminer les 2 semestres selon le niveau
    niveau_code = etudiant.niveau.code
    codes_semestres = SEMESTRES_PAR_NIVEAU.get(niveau_code, [])
    
    if not codes_semestres:
        messages.error(request, f"Niveau {niveau_code} non reconnu !")
        return redirect('bulletins:liste_bulletins')
    
    # Récupérer les objets Semestre
    semestre1 = Semestre.objects.filter(code=codes_semestres[0]).first()
    semestre2 = Semestre.objects.filter(code=codes_semestres[1]).first()
    
    if not semestre1 or not semestre2:
        messages.error(request, "Semestres non trouvés !")
        return redirect('bulletins:liste_bulletins')
    
    # Préparer les données pour le PDF
    data_s1 = preparer_donnees_semestre(etudiant, semestre1)
    data_s2 = preparer_donnees_semestre(etudiant, semestre2)
    
    # Générer le PDF
    pdf_content = generer_pdf_bulletin(etudiant, semestre1, data_s1, semestre2, data_s2)
    
    # Retourner le PDF
    response = HttpResponse(pdf_content, content_type='application/pdf')
    filename = f"Bulletin_{etudiant.nom}_{etudiant.prenom}_{niveau_code}_{etudiant.annee_academique.annee}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def preparer_donnees_semestre(etudiant, semestre):
    """
    Prépare les données d'un semestre pour le PDF
    Retourne : {
        'ues': [...],  # UE avec leurs matières et moyennes
        'matieres_seules': [...]  # Matières sans UE
    }
    """
    donnees = {
        'ues': [],
        'matieres_seules': []
    }
    
    # Récupérer les UE du semestre
    ues = UniteEnseignement.objects.filter(semestre=semestre).prefetch_related('matieres')
    
    for ue in ues:
        matieres_data = []
        
        for matiere in ue.matieres.all():
            try:
                note = Note.objects.get(
                    etudiant=etudiant,
                    matiere=matiere,
                    statut='valide'
                )
                matieres_data.append({
                    'nom': matiere.nom,
                    'moyenne': f"{note.moyenne:.2f}".replace('.', ','),
                    'note_litterale': note.get_note_litterale(),
                    'valide': note.est_valide()
                })
            except Note.DoesNotExist:
                matieres_data.append({
                    'nom': matiere.nom,
                    'moyenne': '—',
                    'note_litterale': '—',
                    'valide': False
                })
        
        # Moyenne UE
        moyenne_ue = ue.calculer_moyenne_ue(etudiant)
        
        donnees['ues'].append({
            'nom': ue.nom,
            'matieres': matieres_data,
            'moyenne': f"{moyenne_ue:.2f}".replace('.', ',') if moyenne_ue > 0 else '—',
            'note_litterale': ue.get_note_litterale_ue(etudiant) if moyenne_ue > 0 else '—',
            'valide': ue.est_valide_ue(etudiant)
        })
    
    # Matières seules (sans UE)
    matieres_seules = Matiere.objects.filter(
        semestre=semestre,
        niveau=etudiant.niveau,
        unites__isnull=True
    )
    
    for matiere in matieres_seules:
        try:
            note = Note.objects.get(
                etudiant=etudiant,
                matiere=matiere,
                statut='valide'
            )
            donnees['matieres_seules'].append({
                'nom': matiere.nom,
                'moyenne': f"{note.moyenne:.2f}".replace('.', ','),
                'note_litterale': note.get_note_litterale(),
                'valide': note.est_valide()
            })
        except Note.DoesNotExist:
            donnees['matieres_seules'].append({
                'nom': matiere.nom,
                'moyenne': '—',
                'note_litterale': '—',
                'valide': False
            })
    
    return donnees


def generer_pdf_bulletin(etudiant, semestre1, data_s1, semestre2, data_s2):
    """Génère le PDF du bulletin avec ReportLab"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1*cm,
        bottomMargin=1.5*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # ===== EN-TÊTE =====
    elements.append(creer_header())
    elements.append(Spacer(1, 0.3*cm))
    
    # ===== TITRE =====
    titre_style = ParagraphStyle(
        'TitreStyle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.white,
        alignment=TA_CENTER,
        spaceAfter=10,
        backColor=colors.grey
    )
    titre = Paragraph("RELEVÉ DE NOTES", titre_style)
    elements.append(titre)
    elements.append(Spacer(1, 0.3*cm))
    
    # ===== INFOS ÉTUDIANT =====
    elements.append(creer_infos_etudiant(etudiant))
    elements.append(Spacer(1, 0.5*cm))
    
    # ===== SEMESTRE 1 =====
    elements.append(creer_tableau_semestre(semestre1, data_s1))
    elements.append(Spacer(1, 0.5*cm))
    
    # ===== SEMESTRE 2 =====
    elements.append(creer_tableau_semestre(semestre2, data_s2))
    elements.append(Spacer(1, 0.5*cm))
    
    # ===== FOOTER =====
    elements.append(creer_footer())
    
    # Construire le PDF
    doc.build(elements)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content
# À AJOUTER dans apps/bulletins/views.py

@login_required
def bulletin_detail(request, etudiant_id):
    """
    Prévisualisation du bulletin avant génération PDF
    Affiche toutes les notes de l'étudiant
    """
    
    # Vérification permission
    if not request.user.profile.is_admin():
        return HttpResponseForbidden("Seul l'Administrateur peut consulter les bulletins !")
    
    # Récupérer l'étudiant
    etudiant = get_object_or_404(Etudiant, pk=etudiant_id)
    
    # Déterminer les 2 semestres selon le niveau
    niveau_code = etudiant.niveau.code
    codes_semestres = SEMESTRES_PAR_NIVEAU.get(niveau_code, [])
    
    if not codes_semestres:
        messages.error(request, f"Niveau {niveau_code} non reconnu !")
        return redirect('bulletins:liste_bulletins')
    
    # Récupérer les objets Semestre
    semestre1 = Semestre.objects.filter(code=codes_semestres[0]).first()
    semestre2 = Semestre.objects.filter(code=codes_semestres[1]).first()
    
    if not semestre1 or not semestre2:
        messages.error(request, "Semestres non trouvés !")
        return redirect('bulletins:liste_bulletins')
    
    # Préparer les données pour affichage
    data_s1 = preparer_donnees_semestre(etudiant, semestre1)
    data_s2 = preparer_donnees_semestre(etudiant, semestre2)
    
    context = {
        'etudiant': etudiant,
        'semestre1': semestre1,
        'data_s1': data_s1,
        'semestre2': semestre2,
        'data_s2': data_s2,
    }
    
    return render(request, 'bulletins/detail.html', context)

def creer_header():
    """Crée l'en-tête du bulletin avec logos"""
    
    # Chemins des logos
# Chemins des logos
    logo_uganc_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_uganc.jpg')
    logo_centre_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_centre_informatique.jpg')
    
    # Styles
    styles = getSampleStyleSheet()
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9)
    
    # Contenu header
    data = [[
        Image(logo_uganc_path, width=3*cm, height=2*cm) if os.path.exists(logo_uganc_path) else '',
        Paragraph("<b>UNIVERSITÉ GAMAL ABDEL<br/>NASSER DE CONAKRY</b><br/>B.P : 1147<br/>Conakry/ R. Guinée", style_center),
        Paragraph("<b>CENTRE INFORMATIQUE</b><br/>Tél : +224 624 08 45 01<br/>+224 657 99 43 57<br/>ibrahima.k.toure@ci.edu.gn", style_center),
        Image(logo_centre_path, width=3*cm, height=2*cm) if os.path.exists(logo_centre_path) else '',
    ]]
    
    table = Table(data, colWidths=[4*cm, 5*cm, 5*cm, 4*cm])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    
    return table


def creer_infos_etudiant(etudiant):
    """Crée le bloc d'informations de l'étudiant"""
    
    styles = getSampleStyleSheet()
    style_left = ParagraphStyle('left', parent=styles['Normal'], fontSize=10)
    
    info_text = f"""
    <b>Étudiante :</b> {etudiant.get_full_name()}<br/>
    <b>Programme :</b> {etudiant.departement.nom}<br/>
    <b>Classe :</b> {etudiant.niveau.nom}<br/>
    <b>Matricule :</b> {etudiant.matricule}<br/>
    <b>Année universitaire :</b> {etudiant.annee_academique.annee}
    """
    
    return Paragraph(info_text, style_left)


def creer_tableau_semestre(semestre, donnees):
    """Crée le tableau des notes pour un semestre avec fusion de cellules pour les UE"""
    
    styles = getSampleStyleSheet()
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName='Helvetica-Bold')
    style_center_normal = ParagraphStyle('center_normal', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9)
    
    # Titre semestre
    titre = Paragraph(f"<b>{semestre.nom}</b>", style_center)
    
    # En-tête tableau
    data = [
        ['MATIÈRES', 'NOTES', 'NOTE LITTÉRALE', 'OBSERV']
    ]
    
    # Liste pour stocker les commandes de fusion
    table_style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alignement vertical au milieu
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]
    
    row_index = 1  # Commence après l'en-tête
    
    # UE
    for ue in donnees['ues']:
        nb_matieres = len(ue['matieres'])
        
        # Nom UE
        data.append([Paragraph(f"<b>{ue['nom']}</b>", styles['Normal']), '', '', ''])
        start_row_ue = row_index
        
        # ENLEVER LA LIGNE VERTICALE à gauche de la colonne NOTES pour la ligne titre UE
        table_style_commands.append(
            ('LINEAFTER', (0, row_index), (0, row_index), 0, colors.white)
        )
        
        row_index += 1
        
        # Matières de l'UE
        for mat in ue['matieres']:
            data.append([
                Paragraph(f"    {mat['nom']}", styles['Normal']),
                mat['moyenne'],
                '',  # Cellule vide, sera fusionnée
                ''   # Cellule vide, sera fusionnée
            ])
            row_index += 1
        
        # Moyenne UE
        data.append([
            Paragraph("<b>Moyenne UE</b>", styles['Normal']),
            Paragraph(f"<b>{ue['moyenne']}</b>", styles['Normal']),
            '',  # Cellule vide, sera fusionnée
            ''   # Cellule vide, sera fusionnée
        ])
        end_row_ue = row_index
        row_index += 1
        
        # FUSION : Seulement si 2+ matières dans l'UE
        if nb_matieres >= 2:
            # Fusionner NOTE LITTÉRALE (colonne 2)
            table_style_commands.append(
                ('SPAN', (2, start_row_ue), (2, end_row_ue))
            )
            
            # Fusionner OBSERV (colonne 3)
            table_style_commands.append(
                ('SPAN', (3, start_row_ue), (3, end_row_ue))
            )
            
            # CENTRER le contenu des cellules fusionnées
            table_style_commands.append(
                ('ALIGN', (2, start_row_ue), (2, end_row_ue), 'CENTER')
            )
            table_style_commands.append(
                ('ALIGN', (3, start_row_ue), (3, end_row_ue), 'CENTER')
            )
            
            # Remplir les cellules fusionnées avec les valeurs CENTRÉES
            data[start_row_ue][2] = Paragraph(ue['note_litterale'], style_center_normal)
            data[start_row_ue][3] = Paragraph('Validé' if ue['valide'] else 'Non-validé', style_center_normal)
        else:
            # Si 1 seule matière, pas de fusion, remplir et centrer normalement
            data[end_row_ue][2] = ue['note_litterale']
            data[end_row_ue][3] = 'Validé' if ue['valide'] else 'Non-validé'
    
    # Matières seules (sans UE)
    for mat in donnees['matieres_seules']:
        data.append([
            Paragraph(f"<b>{mat['nom']}</b>", styles['Normal']),
            mat['moyenne'],
            mat['note_litterale'],
            'Validé' if mat['valide'] else 'Non-validé'
        ])
        row_index += 1
    
    # Créer le tableau
    table = Table(data, colWidths=[8*cm, 3*cm, 3.5*cm, 3.5*cm])
    
    # Appliquer le style avec les fusions
    table.setStyle(TableStyle(table_style_commands))
    
    return Table([[titre], [table]])

def creer_footer():
    """Crée le footer avec date et signatures"""
    
    styles = getSampleStyleSheet()
    style_right = ParagraphStyle('right', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=9)
    style_left = ParagraphStyle('left', parent=styles['Normal'], alignment=TA_LEFT, fontSize=9)
    
    date_aujourdhui = datetime.now().strftime("%d %B %Y")
    
    footer_data = [[
        Paragraph(f"Le DGA/Etudes<br/><br/><br/><b>Dr. Mohamed CONTE</b>", style_left),
        Paragraph(f"Fait à Conakry, le {date_aujourdhui}<br/>Le Directeur Général<br/><br/><br/><b>Dr. Ibrahima Kalil TOURE</b>", style_right),
    ]]
    
    table = Table(footer_data, colWidths=[9*cm, 9*cm])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    return table