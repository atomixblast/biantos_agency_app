from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from .forms import LoginForm


def login_view(request):
    """Vue de connexion"""
    # Si l'utilisateur est déjà connecté, rediriger vers la liste des commandes
    if request.user.is_authenticated:
        return redirect('order:list_orders')
    
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
                next_url = request.GET.get('next', 'order:list_orders')
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
