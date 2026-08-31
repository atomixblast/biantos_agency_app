from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Formulaire de connexion personnalisé"""
    
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary disabled:opacity-50 disabled:pointer-events-none',
            'placeholder': 'votre@email.com',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary disabled:opacity-50 disabled:pointer-events-none',
            'placeholder': '••••••••'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'shrink-0 mt-0.5 border-gray-200 rounded text-primary focus:ring-primary disabled:opacity-50 disabled:pointer-events-none'
        }),
        label="Se souvenir de moi"
    )
