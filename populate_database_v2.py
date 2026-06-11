"""
Script de peuplement de la base de données UGANC
Crée : Départements, Chefs, Niveaux, Années, Semestres, Matières, UE, Enseignants, Étudiants (avec comptes), Notes
"""
import os
import django
import random
from datetime import date
from django.utils import timezone

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.authentication.models import Profile
from apps.gestion_academique.models import (
    Departement, Niveau, AnneeAcademique, Etudiant, Enseignant
)
from apps.structure_pedagogique.models import Semestre, Matiere
from apps.gestion_notes.models import UniteEnseignement, Note

print("=" * 80)
print("🚀 SCRIPT DE PEUPLEMENT DE LA BASE DE DONNÉES UGANC")
print("=" * 80)

# ============================================================================
# 1. DÉPARTEMENTS
# ============================================================================
print("\n📁 Création des départements...")

dept_ntic = Departement.objects.create(
    code='NTIC',
    nom='Nouvelles Technologies de l\'Information et de la Communication',
    description='Département NTIC'
)
print(f"✅ {dept_ntic.nom}")

dept_dl = Departement.objects.create(
    code='DL',
    nom='Développement Logiciel',
    description='Département DL'
)
print(f"✅ {dept_dl.nom}")

departements = [dept_ntic, dept_dl]

# ============================================================================
# 2. CHEFS DE DÉPARTEMENT (NOUVEAU)
# ============================================================================
print("\n👔 Création des chefs de département...")

# Chef NTIC
user_chef_ntic = User.objects.create_user(
    username='CHEF-NTIC',
    password='CHEF-NTIC',
    first_name='Chef',
    last_name='NTIC'
)
user_chef_ntic.profile.role = 'chef_departement'
user_chef_ntic.profile.departement = dept_ntic
user_chef_ntic.profile.save()
print(f"✅ CHEF-NTIC créé (Département NTIC)")

# Chef DL
user_chef_dl = User.objects.create_user(
    username='CHEF-DL',
    password='CHEF-DL',
    first_name='Chef',
    last_name='DL'
)
user_chef_dl.profile.role = 'chef_departement'
user_chef_dl.profile.departement = dept_dl
user_chef_dl.profile.save()
print(f"✅ CHEF-DL créé (Département DL)")

# ============================================================================
# 3. NIVEAUX
# ============================================================================
print("\n📊 Création des niveaux...")

niveau_l1 = Niveau.objects.create(code='L1', nom='Licence 1', ordre=1)
print(f"✅ {niveau_l1.nom}")

niveau_l2 = Niveau.objects.create(code='L2', nom='Licence 2', ordre=2)
print(f"✅ {niveau_l2.nom}")

niveau_l3 = Niveau.objects.create(code='L3', nom='Licence 3', ordre=3)
print(f"✅ {niveau_l3.nom}")

niveaux = [niveau_l1, niveau_l2, niveau_l3]

# ============================================================================
# 4. ANNÉE ACADÉMIQUE
# ============================================================================
print("\n📅 Création de l'année académique...")

annee = AnneeAcademique.objects.create(
    annee='2025-2026',
    date_debut=date(2025, 10, 1),
    date_fin=date(2026, 9, 30),
    est_active=True
)
print(f"✅ {annee.annee} (Active)")

# ============================================================================
# 5. SEMESTRES
# ============================================================================
print("\n📚 Création des semestres...")

semestres_data = [
    ('S1', 'Semestre 1', niveau_l1, 1),
    ('S2', 'Semestre 2', niveau_l1, 2),
    ('S3', 'Semestre 3', niveau_l2, 1),
    ('S4', 'Semestre 4', niveau_l2, 2),
    ('S5', 'Semestre 5', niveau_l3, 1),
    ('S6', 'Semestre 6', niveau_l3, 2),
]

semestres = []
for code, nom, niveau, ordre in semestres_data:
    sem = Semestre.objects.create(
        code=code,
        nom=nom,
        niveau=niveau,
        ordre=ordre
    )
    semestres.append(sem)
    print(f"✅ {nom} ({niveau.code})")

# ============================================================================
# 6. MATIÈRES (7 par semestre = 42 matières)
# ============================================================================
print("\n📖 Création des matières...")

noms_matieres = [
    'Algorithmique', 'Mathématiques', 'Programmation', 'Bases de données',
    'Réseaux informatiques', 'Systèmes d\'exploitation', 'Génie logiciel',
    'Architecture des ordinateurs', 'Programmation web', 'Intelligence artificielle',
    'Sécurité informatique', 'Gestion de projet', 'Analyse de données',
    'Développement mobile', 'Cloud computing', 'Machine Learning'
]

matieres_par_semestre = {}
compteur_matiere = 1

for semestre in semestres:
    matieres_sem = []
    for i in range(7):
        nom_matiere = noms_matieres[(compteur_matiere - 1) % len(noms_matieres)]
        
        matiere = Matiere.objects.create(
            code=f'MAT-{semestre.code}-{i+1:02d}',
            nom=f'{nom_matiere} {semestre.code}',
            coefficient=random.randint(2, 4),
            credits=random.randint(3, 6),
            semestre=semestre,
            niveau=semestre.niveau
        )
        # Assigner aux 2 départements
        matiere.departements.add(dept_ntic, dept_dl)
        matieres_sem.append(matiere)
        compteur_matiere += 1
    
    matieres_par_semestre[semestre] = matieres_sem
    print(f"✅ 7 matières créées pour {semestre.code}")

# ============================================================================
# 7. UNITÉS D'ENSEIGNEMENT (2 UE par semestre = 12 UE)
# ============================================================================
print("\n🎓 Création des UE...")

for semestre in semestres:
    matieres = matieres_par_semestre[semestre]
    
    # UE1 : 2 premières matières
    ue1 = UniteEnseignement.objects.create(
        code=f'UE1-{semestre.code}',
        nom=f'Unité d\'Enseignement 1 - {semestre.code}',
        semestre=semestre
    )
    ue1.matieres.add(*matieres[:2])
    
    # UE2 : matières 3 et 4
    ue2 = UniteEnseignement.objects.create(
        code=f'UE2-{semestre.code}',
        nom=f'Unité d\'Enseignement 2 - {semestre.code}',
        semestre=semestre
    )
    ue2.matieres.add(*matieres[2:4])
    
    print(f"✅ 2 UE créées pour {semestre.code} (4 matières dans UE, 3 libres)")

# ============================================================================
# 8. ENSEIGNANTS (10 par département = 20 enseignants)
# ============================================================================
print("\n👨‍🏫 Création des enseignants...")

grades = ['professeur', 'maitre_conference', 'assistant']
prenoms = ['Mamadou', 'Fatoumata', 'Ibrahima', 'Aissatou', 'Mohamed', 
           'Mariama', 'Ousmane', 'Kadiatou', 'Thierno', 'Hawa']
noms = ['Diallo', 'Bah', 'Sow', 'Camara', 'Barry', 
        'Sylla', 'Keita', 'Conde', 'Toure', 'Kante']

enseignants = []

for dept in departements:
    for i in range(10):
        # Créer user
        username = f'ENS-{dept.code}-{i+1:03d}'
        user = User.objects.create_user(
            username=username,
            password=username,
            first_name=prenoms[i],
            last_name=noms[i]
        )
        
        # Créer enseignant
        enseignant = Enseignant.objects.create(
            code=username,
            nom=noms[i],
            prenom=prenoms[i],
            grade=random.choice(grades),
            specialite=f'Spécialiste {dept.code}',
            email=f'{username.lower()}@uganc.edu.gn'
        )
        enseignant.departements.add(dept)
        
        # Mettre à jour le profil
        user.profile.role = 'enseignant'
        user.profile.enseignant = enseignant
        user.profile.save()
        
        # Assigner 2-3 matières aléatoires du département
        matieres_dept = Matiere.objects.filter(departements=dept, niveau__in=niveaux)
        matieres_assignees = random.sample(list(matieres_dept), min(3, len(matieres_dept)))
        for matiere in matieres_assignees:
            matiere.enseignants.add(enseignant)
        
        enseignants.append(enseignant)
    
    print(f"✅ 10 enseignants créés pour {dept.code}")

# ============================================================================
# 9. ÉTUDIANTS (30 par département = 60 étudiants) + COMPTES USERS
# ============================================================================
print("\n👨‍🎓 Création des étudiants (avec comptes utilisateurs)...")

prenoms_etudiants = [
    'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 
    'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa'
]

etudiants = []
matricule_base = {
    (dept_ntic, niveau_l1): 111,
    (dept_ntic, niveau_l2): 222,
    (dept_ntic, niveau_l3): 333,
    (dept_dl, niveau_l1): 444,
    (dept_dl, niveau_l2): 555,
    (dept_dl, niveau_l3): 666,
}

for dept in departements:
    for niveau in niveaux:
        for i in range(10):
            base = matricule_base[(dept, niveau)]
            matricule = f'{base}-{i+1:03d}-{random.randint(100,999):03d}-{random.randint(100,999):03d}'
            
            # NOUVEAU : Créer le compte utilisateur pour l'étudiant
            user_etudiant = User.objects.create_user(
                username=matricule,
                password=matricule,  # Le matricule est aussi le mot de passe
                first_name=prenoms_etudiants[i],
                last_name=noms[i]
            )
            
            # Créer l'étudiant
            etudiant = Etudiant.objects.create(
                matricule=matricule,
                nom=noms[i],
                prenom=prenoms_etudiants[i],
                date_naissance=date(2000 + random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
                lieu_naissance='Conakry',
                sexe=random.choice(['M', 'F']),
                departement=dept,
                niveau=niveau,
                annee_academique=annee,
                email=f'{matricule.replace("-", "")}@student.uganc.edu.gn',
                statut='actif'
            )
            
            # NOUVEAU : Lier le profil utilisateur à l'étudiant
            user_etudiant.profile.role = 'etudiant'
            user_etudiant.profile.etudiant = etudiant
            user_etudiant.profile.save()
            
            etudiants.append(etudiant)
        
        print(f"✅ 10 étudiants {niveau.code} créés pour {dept.code} (avec comptes)")

print(f"\n✅ Total : {len(etudiants)} étudiants créés")

# ============================================================================
# 10. NOTES
# ============================================================================
print("\n📝 Création des notes...")

total_notes = 0

for etudiant in etudiants:
    # Récupérer les matières du niveau de l'étudiant
    matieres_niveau = Matiere.objects.filter(
        niveau=etudiant.niveau,
        departements=etudiant.departement
    )
    
    # Déterminer le profil de l'étudiant
    rand = random.random()
    if rand < 0.7:  # 70% : bon étudiant
        profil = 'bon'
    elif rand < 0.9:  # 20% : en dette
        profil = 'dette'
    else:  # 10% : notes non validées
        profil = 'non_valide'
    
    nb_matieres_dette = random.randint(1, 2) if profil == 'dette' else 0
    matieres_en_dette = random.sample(list(matieres_niveau), nb_matieres_dette) if nb_matieres_dette > 0 else []
    
    for matiere in matieres_niveau:
        # Choisir un enseignant qui enseigne cette matière
        enseignants_matiere = matiere.enseignants.all()
        if not enseignants_matiere:
            continue
        enseignant = random.choice(enseignants_matiere)
        
        # Générer les notes selon le profil
        if profil == 'bon':
            note1 = round(random.uniform(6, 10), 2)
            note2 = round(random.uniform(6, 10), 2)
            note3 = round(random.uniform(6, 10), 2)
            statut = 'valide'
        elif profil == 'dette' and matiere in matieres_en_dette:
            note1 = round(random.uniform(0, 4), 2)
            note2 = round(random.uniform(0, 4), 2)
            note3 = round(random.uniform(0, 4), 2)
            statut = 'valide'
        elif profil == 'non_valide':
            note1 = round(random.uniform(3, 8), 2)
            note2 = round(random.uniform(3, 8), 2)
            note3 = round(random.uniform(3, 8), 2)
            statut = random.choice(['brouillon', 'soumis'])
        else:  # dette mais pas cette matière
            note1 = round(random.uniform(5, 9), 2)
            note2 = round(random.uniform(5, 9), 2)
            note3 = round(random.uniform(5, 9), 2)
            statut = 'valide'
        
        # Créer la note
        note = Note.objects.create(
            etudiant=etudiant,
            matiere=matiere,
            enseignant=enseignant,
            note1=note1,
            note2=note2,
            note3=note3,
            statut=statut
        )
        
        if statut == 'valide':
            note.date_validation = timezone.now()
            note.save()
        
        total_notes += 1

print(f"✅ {total_notes} notes créées")

# ============================================================================
# RÉSUMÉ
# ============================================================================
print("\n" + "=" * 80)
print("✅ BASE DE DONNÉES PEUPLÉE AVEC SUCCÈS !")
print("=" * 80)
print(f"""
📊 RÉSUMÉ :
  • Départements : {Departement.objects.count()}
  • Chefs de département : 2
  • Niveaux : {Niveau.objects.count()}
  • Années académiques : {AnneeAcademique.objects.count()}
  • Semestres : {Semestre.objects.count()}
  • Matières : {Matiere.objects.count()}
  • UE : {UniteEnseignement.objects.count()}
  • Enseignants : {Enseignant.objects.count()}
  • Étudiants : {Etudiant.objects.count()}
  • Notes : {Note.objects.count()}

👥 COMPTES CRÉÉS :

  🎓 DIRECTION :
        • Direction / Direction123

  👔 CHEFS DE DÉPARTEMENT :
    • CHEF-NTIC / CHEF-NTIC (Département NTIC)
    • CHEF-DL / CHEF-DL (Département DL)

  👨‍🏫 ENSEIGNANTS :
    • ENS-NTIC-001 à ENS-NTIC-010 / [même mot de passe que username]
    • ENS-DL-001 à ENS-DL-010 / [même mot de passe que username]

  👨‍🎓 ÉTUDIANTS (60 comptes) :
    • Matricules comme username ET password
    • Exemples : 111-001-XXX-XXX / 111-001-XXX-XXX
                 222-001-XXX-XXX / 222-001-XXX-XXX
                 333-001-XXX-XXX / 333-001-XXX-XXX
                 etc.

🎯 SCÉNARIO :
  • 70% des étudiants : bonnes notes (validées)
  • 20% des étudiants : en dette (1-2 matières < 5)
  • 10% des étudiants : notes non validées (brouillon/soumis)

🚀 Prêt pour les tests !
""")

print("=" * 80)
