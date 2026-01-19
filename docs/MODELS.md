# 📊 Documentation des Modèles de Données

## Vue d'ensemble

Ce document décrit tous les modèles Django utilisés dans le projet UGANC.

## Relations entre les Modèles

```
User (Django auth)
  └─> Profile (rôle: admin, enseignant, étudiant)

Departement
  └─> Etudiant
  └─> Enseignant (via ManyToMany)

Niveau (L1, L2, L3)
  └─> Etudiant

AnneeAcademique (2025-2026, etc.)
  └─> Etudiant

Matiere
  ├─> Enseignant (via ManyToMany)
  ├─> Niveau (ForeignKey)
  └─> Semestre (ForeignKey)

Note
  ├─> Etudiant (ForeignKey)
  └─> Matiere (ForeignKey)

Bulletin
  ├─> Etudiant (ForeignKey)
  ├─> Semestre (ForeignKey)
  └─> AnneeAcademique (ForeignKey)
```

---

## MODULE 1 : Authentication

### Profile
**Fichier** : `apps/authentication/models.py`

| Champ | Type | Description |
|-------|------|-------------|
| user | OneToOneField(User) | Lien vers User Django |
| role | CharField | 'admin', 'enseignant', 'etudiant' |
| photo | ImageField | Photo de profil (optionnel) |
| telephone | CharField | Numéro de téléphone |
| adresse | TextField | Adresse complète |

**Méthodes** :
- `__str__()` : Retourne le nom complet
- `get_full_name()` : Retourne nom + prénom

---

## MODULE 2 : Gestion Académique

### Departement
**Fichier** : `apps/gestion_academique/models.py`

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | Code unique (ex: NTIC, DL) |
| nom | CharField | Nom complet du département |
| description | TextField | Description |
| created_at | DateTimeField | Date de création |

**Exemple** : NTIC, Développement Logiciel

---

### Niveau
**Fichier** : `apps/gestion_academique/models.py`

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | L1, L2, L3 |
| nom | CharField | Licence 1, 2, 3 |
| ordre | IntegerField | Pour le tri (1, 2, 3) |

---

### AnneeAcademique
**Fichier** : `apps/gestion_academique/models.py`

| Champ | Type | Description |
|-------|------|-------------|
| annee | CharField | "2025-2026" |
| date_debut | DateField | 1er octobre 2025 |
| date_fin | DateField | 30 septembre 2026 |
| est_active | BooleanField | Une seule année active |

---

### Etudiant
**Fichier** : `apps/gestion_academique/models.py`

| Champ | Type | Description |
|-------|------|-------------|
| matricule | CharField | ETU-2025-001 (unique) |
| nom | CharField | Nom de famille |
| prenom | CharField | Prénom |
| date_naissance | DateField | Date de naissance |
| lieu_naissance | CharField | Lieu de naissance |
| sexe | CharField | 'M' ou 'F' |
| departement | ForeignKey(Departement) | Département d'inscription |
| niveau | ForeignKey(Niveau) | Niveau actuel |
| annee_academique | ForeignKey(AnneeAcademique) | Année d'inscription |
| email | EmailField | Email étudiant |
| telephone | CharField | Téléphone |
| photo | ImageField | Photo d'identité |
| adresse | TextField | Adresse complète |
| created_at | DateTimeField | Date d'inscription |

**Méthodes** :
- `__str__()` : Retourne "Matricule - Nom Prénom"
- `get_full_name()` : Nom complet
- `get_age()` : Calcule l'âge

---

### Enseignant
**Fichier** : `apps/gestion_academique/models.py`

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | ENS-001 (unique) |
| nom | CharField | Nom |
| prenom | CharField | Prénom |
| grade | CharField | Professeur, Maître, Assistant, etc. |
| specialite | CharField | Spécialité académique |
| departements | ManyToManyField(Departement) | Peut enseigner dans plusieurs départements |
| email | EmailField | Email professionnel |
| telephone | CharField | Téléphone |
| created_at | DateTimeField | Date d'embauche |

---

## MODULE 4 : Structure Pédagogique

### Semestre
**Fichier** : `apps/structure_pedagogique/models.py`

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | S1, S2 |
| nom | CharField | Semestre 1, Semestre 2 |
| ordre | IntegerField | 1 ou 2 |

---

### Matiere
**Fichier** : `apps/structure_pedagogique/models.py`

| Champ | Type | Description |
|-------|------|-------------|
| code | CharField | MATH101 (unique) |
| nom | CharField | Mathématiques I |
| coefficient | IntegerField | 2, 3, 4, etc. |
| credits | IntegerField | 3, 4, 5, 6, etc. |
| niveau | ForeignKey(Niveau) | Niveau concerné |
| semestre | ForeignKey(Semestre) | Semestre concerné |
| enseignants | ManyToManyField(Enseignant) | Plusieurs enseignants possibles |
| description | TextField | Description du cours |

**Méthodes** :
- `__str__()` : "Code - Nom"

---

## MODULE 3 : Gestion des Notes

### Note
**Fichier** : `apps/gestion_notes/models.py`

| Champ | Type | Description |
|-------|------|-------------|
| etudiant | ForeignKey(Etudiant) | Étudiant concerné |
| matiere | ForeignKey(Matiere) | Matière concernée |
| controle | DecimalField | Note de contrôle (/10) |
| examen | DecimalField | Note d'examen (/10) |
| statut | CharField | 'brouillon' ou 'valide' |
| valide_par | ForeignKey(User) | Enseignant qui a validé |
| valide_le | DateTimeField | Date de validation |
| created_at | DateTimeField | Date de saisie |
| updated_at | DateTimeField | Dernière modification |

**Méthodes** :
- `moyenne()` : Calcule (controle + examen) / 2
- `est_admis()` : True si moyenne >= 5
- `peut_modifier()` : False si statut == 'valide'

**Contraintes** :
- Unique ensemble (etudiant, matiere) : Un seul enregistrement par étudiant/matière
- Validation : 0 <= note <= 10

---

## MODULE 5 : Bulletins & Délibérations

### Resultat
**Fichier** : `apps/bulletins/models.py`

| Champ | Type | Description |
|-------|------|-------------|
| etudiant | ForeignKey(Etudiant) | Étudiant concerné |
| semestre | ForeignKey(Semestre) | Semestre concerné |
| annee_academique | ForeignKey(AnneeAcademique) | Année académique |
| moyenne_generale | DecimalField | Moyenne sur 10 |
| total_credits_obtenus | IntegerField | Crédits validés |
| total_credits_requis | IntegerField | Crédits nécessaires |
| decision | CharField | 'admis' ou 'ajourne' |
| observation | TextField | Commentaire (optionnel) |
| genere_le | DateTimeField | Date de génération |

**Méthodes** :
- `calculer_moyenne()` : Calcule la moyenne pondérée
- `calculer_credits()` : Compte les crédits obtenus
- `determiner_decision()` : Admis si moyenne >= 5

---

### Bulletin
**Fichier** : `apps/bulletins/models.py`

| Champ | Type | Description |
|-------|------|-------------|
| resultat | OneToOneField(Resultat) | Lien vers le résultat |
| fichier_pdf | FileField | PDF généré |
| genere_le | DateTimeField | Date de génération |
| telecharge_le | DateTimeField | Date du dernier téléchargement |
| nombre_telechargements | IntegerField | Compteur |

**Méthodes** :
- `generer_pdf()` : Génère le bulletin PDF
- `get_absolute_url()` : URL de téléchargement

---

## Règles Métier

### Règle 1 : Validation des Notes
- Les notes sont saisies en mode "brouillon"
- L'enseignant peut modifier tant que statut = "brouillon"
- Une fois validées (statut = "valide"), les notes ne peuvent plus être modifiées
- Seul l'enseignant de la matière peut saisir/valider

### Règle 2 : Calcul de la Moyenne
```python
moyenne_matiere = (controle + examen) / 2
```

### Règle 3 : Moyenne Générale
```python
somme = sum(note.moyenne() * matiere.coefficient for note in notes)
total_coefficients = sum(matiere.coefficient for matiere in matieres)
moyenne_generale = somme / total_coefficients
```

### Règle 4 : Décision Finale
```python
if moyenne_generale >= 5:
    decision = "ADMIS"
else:
    decision = "AJOURNE"
```

### Règle 5 : Crédits
- Un étudiant obtient les crédits d'une matière si sa moyenne >= 5
- Les crédits sont cumulables d'un semestre à l'autre

---

## Exemples d'Utilisation

### Créer un étudiant
```python
from apps.gestion_academique.models import Etudiant, Departement, Niveau

etudiant = Etudiant.objects.create(
    matricule="ETU-2025-001",
    nom="DIALLO",
    prenom="Mamadou",
    departement=Departement.objects.get(code="NTIC"),
    niveau=Niveau.objects.get(code="L1")
)
```

### Saisir une note
```python
from apps.gestion_notes.models import Note
from apps.structure_pedagogique.models import Matiere

note = Note.objects.create(
    etudiant=etudiant,
    matiere=Matiere.objects.get(code="MATH101"),
    controle=7.5,
    examen=8.0,
    statut='brouillon'
)

print(note.moyenne())  # 7.75
print(note.est_admis())  # True
```

### Calculer les résultats
```python
from apps.bulletins.models import Resultat

resultat = Resultat.objects.create(
    etudiant=etudiant,
    semestre=semestre,
    annee_academique=annee
)

resultat.calculer_moyenne()
resultat.calculer_credits()
resultat.determiner_decision()
resultat.save()
```

---

## Migrations

Après avoir créé/modifié les modèles :

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Vérifier les migrations
python manage.py showmigrations
```

---

**Bon développement ! 🚀**
