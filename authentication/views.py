from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm


def login_view(request):
    """Vue de connexion"""
    # Si l'utilisateur est déjà connecté, rediriger vers la page d'accueil
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            # Authentifier l'utilisateur
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Gérer "Se souvenir de moi"
                if not remember_me:
                    # Session expire à la fermeture du navigateur
                    request.session.set_expiry(0)
                else:
                    # Session expire après 2 semaines
                    request.session.set_expiry(1209600)  # 2 semaines en secondes
                
                messages.success(request, f"Bienvenue {user.username} !")
                
                # Rediriger vers la page demandée ou la liste des commandes
                # (on n'accepte qu'une URL interne, pour éviter les redirections externes)
                next_url = request.GET.get('next')
                if not next_url or not url_has_allowed_host_and_scheme(
                        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                    next_url = settings.LOGIN_REDIRECT_URL
                return redirect(next_url)
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = LoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})


@login_required
def logout_view(request):
    """Vue de déconnexion"""
    username = request.user.username
    logout(request)
    messages.success(request, f"Au revoir {username}, à bientôt !")
    return redirect('authentication:login')
