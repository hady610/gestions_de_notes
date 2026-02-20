# authentication/views.py
"""
MODULE 1 : Authentication - Views
Fichier : apps/authentication/views.py
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from .forms import LoginForm, ProfileForm, UserRegistrationForm


# ===== HOME VIEW (Dashboard selon rôle) =====

@login_required
def home_view(request):
    """
    Page d'accueil - Affiche un dashboard selon le rôle de l'utilisateur
    """
    from apps.gestion_academique.models import Departement, Niveau, Etudiant, Enseignant
    from apps.structure_pedagogique.models import Matiere, Semestre

    context = {
        'user': request.user,
        'profile': request.user.profile,
    }

    # ===== ADMIN (Doyen) =====
    if request.user.profile.is_admin():
        context.update({
            'nb_etudiants': Etudiant.objects.count(),
            'nb_enseignants': Enseignant.objects.count(),
            'nb_departements': Departement.objects.count(),
            'nb_matieres': Matiere.objects.count(),
        })

    # ===== CHEF DE DÉPARTEMENT =====
    elif request.user.profile.is_chef_departement():
        dept = request.user.profile.departement
        context.update({
            'departement': dept,
            'nb_etudiants': Etudiant.objects.filter(departement=dept).count(),
            'nb_enseignants': Enseignant.objects.filter(departements=dept).count(),
            'nb_matieres': Matiere.objects.filter(departements=dept).count(),
        })

    # ===== DIRECTEUR DU PROGRAMME =====
        # ===== DIRECTEUR DU PROGRAMME =====
    elif request.user.profile.is_chef_departement():
        departement = request.user.profile.departement
        
        # Stats filtrées par département
        nb_matieres = Matiere.objects.filter(departements=departement).distinct().count()
        nb_enseignants = Enseignant.objects.filter(departements=departement).distinct().count()
        nb_etudiants = Etudiant.objects.filter(departement=departement).count()
        nb_niveaux = Niveau.objects.count()
        
        context.update({
            'departement': departement,
            'nb_matieres': nb_matieres,
            'nb_enseignants': nb_enseignants,
            'nb_etudiants': nb_etudiants,
            'nb_niveaux': nb_niveaux,
        })

    # ===== ENSEIGNANT =====
    elif request.user.profile.is_enseignant():
        enseignant = request.user.profile.enseignant
        if enseignant:
            matieres = Matiere.objects.filter(enseignants=enseignant)
            context.update({
                'enseignant': enseignant,
                'matieres': matieres,
                'nb_matieres': matieres.count(),
            })

    # ===== ÉTUDIANT =====
    elif request.user.profile.is_etudiant():
        etudiant = request.user.profile.etudiant
        if etudiant:
            context.update({
                'etudiant': etudiant,
            })

    return render(request, 'home.html', context)


# ===== LOGIN / LOGOUT =====

def login_view(request):
    """
    Vue de connexion - commune aux 5 rôles
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Message de bienvenue
                nom_complet = user.get_full_name() or user.username
                messages.success(request, f'Bienvenue {nom_complet} !')

                # Message changez votre password si première connexion
                if hasattr(user, 'profile') and user.profile.is_first_login:
                    messages.warning(request, 'Changez votre mot de passe par défaut pour plus de sécurité !')
                    user.profile.is_first_login = False
                    user.profile.save()

                return redirect('home')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = LoginForm()

    context = {
        'form': form,
        'page_title': 'Connexion - UGANC'
    }

    return render(request, 'authentication/login.html', context)


def logout_view(request):
    """
    Vue de déconnexion
    """
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('authentication:login')


# ===== PROFIL =====

@login_required
def profile_view(request):
    """
    Vue du profil utilisateur
    """
    context = {
        'user': request.user,
        'profile': request.user.profile,
        'page_title': 'Mon Profil'
    }

    return render(request, 'authentication/profile.html', context)


@login_required
def profile_edit_view(request):
    """
    Vue d'édition du profil
    """
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('authentication:profile')
    else:
        form = ProfileForm(instance=request.user.profile)

    context = {
        'form': form,
        'page_title': 'Modifier mon Profil'
    }

    return render(request, 'authentication/profile_edit.html', context)


# ===== CHANGER MOT DE PASSE =====

@login_required
def change_password_view(request):
    """
    Vue de changement de mot de passe
    """
    if request.method == 'POST':
        ancien_password = request.POST.get('ancien_password')
        nouveau_password = request.POST.get('nouveau_password')
        confirmer_password = request.POST.get('confirmer_password')

        # Vérifier ancien password
        if not request.user.check_password(ancien_password):
            messages.error(request, 'Ancien mot de passe incorrect !')
            return redirect('authentication:change_password')

        # Vérifier que les 2 nouveaux passwords sont identiques
        if nouveau_password != confirmer_password:
            messages.error(request, 'Les deux mots de passe ne correspondent pas !')
            return redirect('authentication:change_password')

        # Vérifier la longueur
        if len(nouveau_password) < 6:
            messages.error(request, 'Le mot de passe doit avoir au moins 6 caractères !')
            return redirect('authentication:change_password')

        # Changer le password
        request.user.set_password(nouveau_password)
        request.user.save()

        messages.success(request, 'Mot de passe changé avec succès !')
        return redirect('authentication:profile')

    return render(request, 'authentication/change_password.html', {'page_title': 'Changer mot de passe'})


# ===== CRÉER COMPTES =====

@login_required
def create_etudiant_account(request):
    """
    Créer un compte pour un étudiant
    Username = matricule, Password = matricule
    """
    if not (request.user.profile.is_admin() or request.user.profile.is_chef_departement()):
        messages.error(request, "Vous n'avez pas la permission !")
        return redirect('home')

    from apps.gestion_academique.models import Etudiant

    if request.method == 'POST':
        etudiant_id = request.POST.get('etudiant_id')
        etudiant = Etudiant.objects.get(pk=etudiant_id)

        if User.objects.filter(username=etudiant.matricule).exists():
            messages.error(request, f'Le compte pour {etudiant.matricule} existe déjà !')
            return redirect('authentication:create_etudiant_account')

        # Créer le compte
        user = User.objects.create_user(
            username=etudiant.matricule,
            password=etudiant.matricule,
            first_name=etudiant.prenom,
            last_name=etudiant.nom,
            email=etudiant.email or ''
        )

        user.profile.role = 'etudiant'
        user.profile.etudiant = etudiant
        user.profile.is_first_login = True
        user.profile.save()

        messages.success(request, f'Compte créé pour {etudiant.get_full_name()} ! Username: {etudiant.matricule}')
        return redirect('authentication:create_etudiant_account')

    # Étudiants sans compte
    etudiants_sans_compte = Etudiant.objects.exclude(user_profile__isnull=False)

    context = {
        'etudiants': etudiants_sans_compte,
        'page_title': 'Créer comptes étudiants'
    }
    return render(request, 'authentication/create_etudiant_account.html', context)


@login_required
def create_enseignant_account(request):
    """
    Créer un compte pour un enseignant
    Username = code, Password = code
    """
    if not (request.user.profile.is_admin() or request.user.profile.is_chef_departement()):
        messages.error(request, "Vous n'avez pas la permission !")
        return redirect('home')

    from apps.gestion_academique.models import Enseignant

    if request.method == 'POST':
        enseignant_id = request.POST.get('enseignant_id')
        enseignant = Enseignant.objects.get(pk=enseignant_id)

        if User.objects.filter(username=enseignant.code).exists():
            messages.error(request, f'Le compte pour {enseignant.code} existe déjà !')
            return redirect('authentication:create_enseignant_account')

        # Créer le compte
        user = User.objects.create_user(
            username=enseignant.code,
            password=enseignant.code,
            first_name=enseignant.prenom,
            last_name=enseignant.nom,
            email=enseignant.email or ''
        )

        user.profile.role = 'enseignant'
        user.profile.enseignant = enseignant
        user.profile.is_first_login = True
        user.profile.save()

        messages.success(request, f'Compte créé pour {enseignant.get_full_name()} ! Username: {enseignant.code}')
        return redirect('authentication:create_enseignant_account')

    # Enseignants sans compte
    enseignants_sans_compte = Enseignant.objects.exclude(user_profile__isnull=False)

    context = {
        'enseignants': enseignants_sans_compte,
        'page_title': 'Créer comptes enseignants'
    }
    return render(request, 'authentication/create_enseignant_account.html', context)


# ===== INSCRIPTION =====

def register_view(request):
    """
    Vue d'inscription
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            messages.success(request, 'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.')
            return redirect('authentication:login')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
        'page_title': 'Inscription'
    }

    return render(request, 'authentication/register.html', context)


# ===== RÉINITIALISATION MOT DE PASSE =====

def password_reset_view(request):
    """
    Réinitialiser le mot de passe oublié
    """
    import random
    import string
    
    if request.method == 'POST':
        username = request.POST.get('username')
        
        try:
            # Chercher l'utilisateur
            user = User.objects.get(username=username)
            
            # Générer un nouveau mot de passe temporaire (8 caractères)
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Changer le mot de passe
            user.set_password(new_password)
            user.save()
            
            # Marquer comme première connexion pour forcer le changement
            user.profile.is_first_login = True
            user.profile.save()
            
            messages.success(request, f'Mot de passe réinitialisé pour {username} !')
            
            context = {
                'new_password': new_password,
                'username': username,
                'page_title': 'Mot de passe réinitialisé'
            }
            return render(request, 'authentication/password_reset.html', context)
            
        except User.DoesNotExist:
            messages.error(request, f"Aucun utilisateur trouvé avec le nom d'utilisateur '{username}'")
            return redirect('authentication:password_reset')
    
    context = {
        'page_title': 'Réinitialiser mot de passe'
    }
    return render(request, 'authentication/password_reset.html', context)
