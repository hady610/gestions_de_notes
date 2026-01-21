# authentication/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from .forms import LoginForm, ProfileForm, UserRegistrationForm


def login_view(request):
    """
    Vue de connexion
    """
    # Si déjà connecté, rediriger selon le rôle
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            if request.user.profile.is_admin():
                return redirect('home')
            elif request.user.profile.is_enseignant():
                return redirect('home')
            else:
                return redirect('home')
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Message de bienvenue personnalisé
                nom_complet = user.get_full_name() or user.username
                messages.success(request, f'Bienvenue {nom_complet} !')
                
                # Redirection selon le rôle
                if hasattr(user, 'profile'):
                    if user.profile.is_admin():
                        return redirect('home')
                    elif user.profile.is_enseignant():
                        return redirect('home')
                    else:
                        return redirect('home')
                
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


def register_view(request):
    """
    Vue d'inscription (optionnel - peut être désactivé en production)
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Le profil est créé automatiquement par le signal
            messages.success(request, 'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.')
            return redirect('authentication:login')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Inscription'
    }
    
    return render(request, 'authentication/register.html', context)
