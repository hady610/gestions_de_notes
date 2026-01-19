# 📝 Guide de Contribution

## 🎯 Pour les Membres de l'Équipe

Bienvenue dans le projet UGANC ! Ce document explique comment contribuer efficacement.

## 🚀 Démarrage Rapide

### 1. Configuration Initiale

```bash
# Cloner le projet
git clone https://github.com/votre-org/uganc-gestion-notes.git
cd uganc-gestion-notes

# Créer votre environnement virtuel
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
# Éditer .env si nécessaire

# Initialiser la base de données
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Charger les données de test
python manage.py loaddata fixtures/initial_data.json

# Lancer le serveur
python manage.py runserver
```

### 2. Workflow Git

#### a) Créer votre branche

**Format** : `module-X/description-courte`

```bash
# Exemples selon votre module
git checkout -b module-1/authentication-login
git checkout -b module-2/crud-etudiants
git checkout -b module-3/saisie-notes
git checkout -b module-4/gestion-matieres
git checkout -b module-5/generation-bulletins
```

#### b) Travailler sur votre module

```bash
# 1. Assurez-vous d'être sur votre branche
git branch  # Affiche la branche actuelle

# 2. Faites vos modifications
# ... éditez vos fichiers ...

# 3. Vérifiez ce qui a changé
git status

# 4. Ajoutez vos fichiers
git add .

# 5. Committez avec le bon format
git commit -m "[MODULE-X] Description courte

Description détaillée de ce qui a été fait"

# Exemple:
git commit -m "[MODULE-2] Ajout CRUD étudiants

- Modèle Etudiant créé avec tous les champs
- Views: List, Create, Update, Delete
- Templates HTML avec Bootstrap
- Tests unitaires basiques"

# 6. Poussez sur GitHub
git push origin module-X/votre-feature
```

#### c) Créer une Pull Request

1. Allez sur GitHub
2. Cliquez sur "Pull Request"
3. Base: `develop` ← Compare: `votre-branche`
4. Titre: `[MODULE-X] Description`
5. Description détaillée de vos changements
6. Assignez au moins 1 revieweur
7. Créez la PR

#### d) Après le merge

```bash
# Revenez sur develop
git checkout develop

# Mettez à jour
git pull origin develop

# Supprimez votre ancienne branche
git branch -d module-X/votre-feature
```

## 📋 Règles de Code

### Structure d'un Module Django

```
apps/votre_module/
├── __init__.py
├── models.py          # Modèles de données
├── views.py           # Vues (logique métier)
├── forms.py           # Formulaires Django
├── urls.py            # URLs du module
├── admin.py           # Interface admin
├── tests.py           # Tests unitaires
├── migrations/        # Migrations de base de données
└── templates/
    └── votre_module/
        ├── list.html
        ├── detail.html
        ├── form.html
        └── confirm_delete.html
```

### Convention de Nommage

#### Models
```python
class Etudiant(models.Model):  # Singulier, CamelCase
    pass

class AnneeAcademique(models.Model):
    pass
```

#### Views
```python
# Function-based views
def liste_etudiants(request):
    pass

# Class-based views (préféré)
class EtudiantListView(ListView):
    pass

class EtudiantCreateView(CreateView):
    pass
```

#### URLs
```python
urlpatterns = [
    path('etudiants/', views.liste_etudiants, name='liste_etudiants'),
    path('etudiants/ajouter/', views.ajouter_etudiant, name='ajouter_etudiant'),
]
```

#### Templates
```
liste_etudiants.html
detail_etudiant.html
form_etudiant.html
confirm_delete_etudiant.html
```

### Code Style

#### Imports
```python
# Standard library
import os
from datetime import datetime

# Django
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Third-party
from PIL import Image

# Local
from apps.gestion_academique.models import Etudiant
```

#### Docstrings
```python
def calculer_moyenne(notes):
    """
    Calcule la moyenne d'une liste de notes.
    
    Args:
        notes (list): Liste de notes (float ou int)
    
    Returns:
        float: La moyenne calculée
    
    Raises:
        ValueError: Si la liste est vide
    """
    if not notes:
        raise ValueError("La liste de notes ne peut pas être vide")
    return sum(notes) / len(notes)
```

## ✅ Checklist Avant de Pusher

- [ ] Le code fonctionne localement
- [ ] Les migrations sont créées (`python manage.py makemigrations`)
- [ ] Les migrations sont appliquées (`python manage.py migrate`)
- [ ] Pas d'erreur dans la console
- [ ] Les templates sont bien liés
- [ ] Les URLs fonctionnent
- [ ] Le code est commenté (si nécessaire)
- [ ] Les tests passent (si vous en avez écrits)
- [ ] `.env` n'est PAS dans le commit
- [ ] Pas de `print()` de debug oubliés

## 🧪 Tests

### Lancer les tests
```bash
# Tous les tests
python manage.py test

# Tests d'un module
python manage.py test apps.gestion_academique

# Un test spécifique
python manage.py test apps.gestion_academique.tests.TestEtudiantModel
```

### Écrire un test simple
```python
# tests.py
from django.test import TestCase
from .models import Etudiant

class EtudiantTestCase(TestCase):
    def setUp(self):
        """Exécuté avant chaque test"""
        Etudiant.objects.create(
            matricule="ETU-001",
            nom="DIALLO",
            prenom="Mamadou"
        )
    
    def test_etudiant_creation(self):
        """Test de création d'un étudiant"""
        etudiant = Etudiant.objects.get(matricule="ETU-001")
        self.assertEqual(etudiant.nom, "DIALLO")
```

## 🆘 Problèmes Courants

### Erreur: "No module named 'apps'"
```bash
# Assurez-vous d'être dans le bon dossier
cd uganc-gestion-notes

# Vérifiez que manage.py est présent
ls manage.py
```

### Erreur: "Table doesn't exist"
```bash
# Créez les migrations
python manage.py makemigrations

# Appliquez-les
python manage.py migrate
```

### Erreur: "Port already in use"
```bash
# Utilisez un autre port
python manage.py runserver 8001
```

### Conflit Git
```bash
# Mettez à jour develop
git checkout develop
git pull origin develop

# Revenez sur votre branche
git checkout votre-branche

# Récupérez les changements
git rebase develop

# En cas de conflit, résolvez-les puis:
git add .
git rebase --continue
```

## 💬 Communication

### Daily Stand-up (Optionnel)
Chaque matin (ou soir), postez dans le groupe :
```
[MODULE-X] Update
✅ Fait hier: Description
🔄 Aujourd'hui: Ce que je vais faire
❌ Blocages: Si vous êtes bloqué
```

### Demander de l'Aide
```
[MODULE-X] Question: Titre de la question

Description détaillée du problème
Code concerné (si applicable)
Message d'erreur (si applicable)
```

### Signaler un Blocage
```
[MODULE-X] 🚨 BLOCAGE: Titre

Description du blocage
Impact sur le planning
Besoin d'aide de: (quel module/personne)
```

## 📅 Planning de Développement

### Semaine 1 (6-12 Jan)
- Module 1: 100% - Authentication complète
- Module 2: 60% - Structures de base
- Module 4: 80% - Matières créées

### Semaine 2 (13-19 Jan)
- Module 2: 100% - Terminé
- Module 4: 100% - Terminé
- Module 3: 70% - Saisie notes OK

### Semaine 3 (20-26 Jan)
- Module 3: 100% - Terminé
- Module 5: 90% - PDF à finaliser
- Tests d'intégration

### Semaine 4 (27-31 Jan)
- Module 5: 100% - Terminé
- Corrections bugs
- Documentation finale

## 🎯 Objectifs par Module

### MODULE 1 - Authentication
- [ ] Modèle User/Profile avec rôles
- [ ] Login/Logout fonctionnel
- [ ] Middleware de permissions
- [ ] Templates de connexion

### MODULE 2 - Gestion Académique
- [ ] CRUD Étudiants complet
- [ ] CRUD Enseignants complet
- [ ] Gestion Départements/Niveaux
- [ ] Gestion Années académiques

### MODULE 3 - Gestion Notes
- [ ] Modèle Note avec validation
- [ ] Interface de saisie
- [ ] Système brouillon/validé
- [ ] Contrôles 0-10

### MODULE 4 - Structure Pédagogique
- [ ] CRUD Matières
- [ ] Gestion Semestres
- [ ] Coefficients et crédits
- [ ] Association matière-enseignant

### MODULE 5 - Bulletins
- [ ] Calcul des moyennes
- [ ] Règle Admis/Ajourné (≥5)
- [ ] Génération PDF
- [ ] Historique résultats

## 🏆 Bonnes Pratiques

1. **Committez souvent** : Petits commits fréquents > gros commits rares
2. **Testez localement** : Toujours avant de pusher
3. **Communiquez** : Signalez vos avancements et blocages
4. **Reviewez** : Regardez les PRs des autres modules
5. **Documentez** : Commentez le code complexe
6. **Respectez les deadlines** : Chaque semaine compte !

## ❓ Questions ?

Contactez :
- Le chef de projet
- Le responsable de votre module
- Posez dans le chat de l'équipe

---

**Bon courage à tous ! 💪🚀**
