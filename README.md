
# 🎓 UGANC - Système de Gestion des Notes

**Université Gamal Abdel Nasser de Conakry**  
Faculté Centre Informatique - Départements NTIC & Développement Logiciel

## 📋 Description

Système complet de gestion des notes académiques permettant :
- Gestion des utilisateurs et sécurité (Module 1)
- Gestion académique (étudiants, enseignants, départements) (Module 2)
- Saisie et validation des notes (Module 3)
- Structure pédagogique (matières, semestres, programmes) (Module 4)
- Génération de bulletins et délibérations (Module 5)

## 🛠️ Technologies

- **Backend** : Django 5.0.1
- **Base de données** : PostgreSQL (production), SQLite (développement)
- **Frontend** : Bootstrap 5 + Templates Django
- **PDF** : ReportLab
- **Python** : 3.11

## 📦 Installation

### Prérequis
- Python 3.11
- pip
- virtualenv (recommandé)
- PostgreSQL (pour la production)

### Étapes d'installation

```bash
# 1. Cloner le repository
git clone https://github.com/votre-org/uganc-gestion-notes.git
cd uganc-gestion-notes

# 2. Créer un environnement virtuel
python3.11 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos configurations

# 5. Créer la base de données
python manage.py makemigrations
python manage.py migrate

# 6. Créer un superutilisateur
python manage.py createsuperuser

# 7. Charger les données de test (optionnel)
python manage.py loaddata fixtures/initial_data.json

# 8. Lancer le serveur de développement
python manage.py runserver
```

Accédez à : http://127.0.0.1:8000

## 🏗️ Structure du Projet

```
uganc-gestion-notes/
├── config/                      # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── authentication/          # MODULE 1 - Utilisateurs & Sécurité
│   ├── gestion_academique/      # MODULE 2 - Étudiants, Enseignants, etc.
│   ├── gestion_notes/           # MODULE 3 - Saisie et validation notes
│   ├── structure_pedagogique/   # MODULE 4 - Matières, Semestres
│   └── bulletins/               # MODULE 5 - Bulletins & Résultats
├── static/                      # Fichiers statiques (CSS, JS, images)
├── media/                       # Fichiers uploadés (photos, etc.)
├── templates/                   # Templates HTML partagés
├── fixtures/                    # Données de test
├── docs/                        # Documentation
├── requirements.txt             # Dépendances Python
├── manage.py                    # Script Django
└── .env.example                 # Exemple de configuration
```

## 👥 Organisation des Modules

### Module 1 : Authentication (3 personnes)
**Chef de module** : [À définir]
- Modèles : User, Profile (rôle: admin, enseignant, étudiant)
- Vues : Login, Logout, Register, Profil
- Middleware : Vérification des permissions

### Module 2 : Gestion Académique (3 personnes)
**Chef de module** : [À définir]
- Modèles : Etudiant, Enseignant, Departement, Niveau, AnneeAcademique
- Vues : CRUD complet pour chaque entité
- Gestion des inscriptions

### Module 3 : Gestion des Notes (3 personnes)
**Chef de module** : [À définir]
- Modèles : Note (avec statut brouillon/validé)
- Vues : Saisie, modification, validation
- Règles : Notes entre 0 et 10, validation définitive

### Module 4 : Structure Pédagogique (3 personnes)
**Chef de module** : [À définir]
- Modèles : Matiere, Semestre, Programme
- Vues : Gestion matières, coefficients, crédits
- Association matière → enseignant → niveau

### Module 5 : Bulletins & Délibérations (3 personnes)
**Chef de module** : [À définir]
- Modèles : Bulletin, Resultat
- Vues : Calcul moyennes, génération PDF
- Règle : Moyenne ≥ 5 = Admis, < 5 = Ajourné

## 🔄 Workflow Git

### Branches
- `main` : Production (NE PAS TOUCHER directement)
- `develop` : Intégration (merge des modules)
- `module-X/feature-name` : Branches de travail

### Convention de nommage
```
module-1/authentication-login
module-2/crud-etudiants
module-3/validation-notes
module-4/gestion-matieres
module-5/generation-pdf
```

### Commits
```
[MODULE-X] Description courte

Description détaillée

Exemple:
[MODULE-2] Ajout du CRUD étudiants

- Modèle Etudiant créé
- Vues List, Create, Update, Delete
- Templates HTML
- Tests unitaires
```

## 🧪 Tests

```bash
# Lancer tous les tests
python manage.py test

# Tests d'un module spécifique
python manage.py test apps.gestion_academique

# Tests avec couverture
coverage run --source='.' manage.py test
coverage report
```

## 📚 Documentation

- [Modèles de données](docs/MODELS.md)
- [Guide de contribution](CONTRIBUTING.md)
- [Règles métier](docs/BUSINESS_RULES.md)
- [Guide de déploiement](docs/DEPLOYMENT.md)

## 🚀 Déploiement

### Variables d'environnement (Production)
```env
DEBUG=False
SECRET_KEY=votre-clé-secrète-forte
DATABASE_URL=postgres://user:password@host:5432/dbname
ALLOWED_HOSTS=votre-domaine.com
```

### Collecte des fichiers statiques
```bash
python manage.py collectstatic
```

## 👨‍💻 Contributeurs

### Équipe de développement (15 personnes)

**Module 1 - Authentication**
- Personne 1
- Personne 2
- Personne 3

**Module 2 - Gestion Académique**
- Personne 4
- Personne 5
- Personne 6

**Module 3 - Gestion des Notes**
- Personne 7
- Personne 8
- Personne 9

**Module 4 - Structure Pédagogique**
- Personne 10
- Personne 11
- Personne 12

**Module 5 - Bulletins**
- Personne 13
- Personne 14
- Personne 15

**Chef de Projet** : [Ton nom]

## 📝 Licence

Projet académique - UGANC 2026

## 📞 Contact

Pour toute question, contactez le chef de projet ou créez une issue sur GitHub.

---

**Bonne chance à toute l'équipe ! 🚀**
