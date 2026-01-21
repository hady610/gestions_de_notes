# authentication/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile


class LoginForm(forms.Form):
    """
    Formulaire de connexion
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nom d\'utilisateur',
            'autofocus': True
        }),
        label='Nom d\'utilisateur'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Mot de passe'
        }),
        label='Mot de passe'
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Se souvenir de moi'
    )


class ProfileForm(forms.ModelForm):
    """
    Formulaire d'édition du profil
    """
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        }),
        label='Prénom'
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom de famille'
        }),
        label='Nom'
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemple@ugac.edu.gn'
        }),
        label='Email'
    )
    
    class Meta:
        model = Profile
        fields = ['photo', 'telephone', 'adresse']
        widgets = {
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+224 XXX XX XX XX'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse complète'
            }),
        }
        labels = {
            'photo': 'Photo de profil',
            'telephone': 'Téléphone',
            'adresse': 'Adresse'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialiser les champs User
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Mettre à jour les infos du User
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            profile.save()
        
        return profile


class UserRegistrationForm(forms.ModelForm):
    """
    Formulaire d'inscription (optionnel)
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        }),
        label='Mot de passe',
        min_length=8
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez le mot de passe'
        }),
        label='Confirmer le mot de passe'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemple@ugac.edu.gn'
            }),
        }
        labels = {
            'username': 'Nom d\'utilisateur',
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email'
        }
    
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Les mots de passe ne correspondent pas.')
        
        return password_confirm
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Cet email est déjà utilisé.')
        return email