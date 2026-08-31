# 🔐 Guide d'Authentification - Biantos Agency

## 📋 Vue d'ensemble

Le système d'authentification permet aux utilisateurs de se connecter et de gérer leur session de manière sécurisée.

## 🚀 Fonctionnalités

### 1. Page de Connexion
**URL** : `/auth/login/`

**Caractéristiques** :
- ✅ Design moderne et responsive
- ✅ Authentification par email et mot de passe
- ✅ Option "Se souvenir de moi" (session de 2 semaines)
- ✅ Messages d'erreur clairs
- ✅ Redirection automatique après connexion
- ✅ Protection contre les utilisateurs déjà connectés

**Champs du formulaire** :
- **Email** : Adresse email de l'utilisateur
- **Mot de passe** : Mot de passe sécurisé
- **Se souvenir de moi** : Prolonge la session à 2 semaines

### 2. Déconnexion
**URL** : `/auth/logout/`

**Fonctionnement** :
- Déconnecte l'utilisateur
- Affiche un message de confirmation
- Redirige vers la page de connexion

### 3. Protection des Pages

Les pages nécessitant une authentification :
- ✅ Liste des commandes (`@login_required`)
- ✅ Création de commande
- ✅ Mise à jour de commande
- ✅ Détail de commande
- ✅ Déconnexion

## 🔧 Configuration

### Settings Django (`settings.py`)

```python
# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'authentication.User'

# URLs de redirection
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/order/list_orders/'
LOGOUT_REDIRECT_URL = '/auth/login/'
```

### Modèle User Personnalisé

Le système utilise un modèle `User` personnalisé avec :
- **Email** comme identifiant principal (USERNAME_FIELD)
- **Username** comme champ requis
- Héritage de `AbstractUser` de Django

## 📝 Utilisation

### Créer un utilisateur (via shell)

```bash
python manage.py shell
```

```python
from authentication.models import User

# Créer un superutilisateur
User.objects.create_superuser(
    email='admin@biantos.com',
    username='admin',
    password='votre_mot_de_passe'
)

# Créer un utilisateur normal
User.objects.create_user(
    email='user@biantos.com',
    username='user',
    password='votre_mot_de_passe'
)
```

### Créer un superutilisateur (via commande)

```bash
python manage.py createsuperuser
```

## 🎨 Interface Utilisateur

### Page de Connexion
- Design avec gradient de fond
- Logo de l'entreprise
- Formulaire centré et moderne
- Messages d'erreur/succès colorés
- Icônes Material Design

### Header (Utilisateur connecté)
- Avatar de l'utilisateur
- Nom d'utilisateur et email
- Menu déroulant avec :
  - Profil
  - Paramètres
  - **Déconnexion** (en rouge)

## 🔒 Sécurité

### Mesures de Sécurité Implémentées

1. **Protection CSRF** : Tous les formulaires incluent un token CSRF
2. **Hachage des mots de passe** : Utilisation du système de hachage de Django
3. **Session sécurisée** : 
   - Sans "Se souvenir de moi" : expire à la fermeture du navigateur
   - Avec "Se souvenir de moi" : expire après 2 semaines
4. **Redirection sécurisée** : Vérification du paramètre `next`
5. **Messages utilisateur** : Retour d'information clair sans révéler d'informations sensibles

## 🔄 Flux d'Authentification

### Connexion Réussie
```
1. Utilisateur accède à /auth/login/
2. Saisit email et mot de passe
3. Soumet le formulaire
4. Système vérifie les credentials
5. Crée une session
6. Redirige vers /order/list_orders/
```

### Accès à une Page Protégée (Non Connecté)
```
1. Utilisateur accède à /order/list_orders/
2. Système détecte l'absence d'authentification
3. Redirige vers /auth/login/?next=/order/list_orders/
4. Après connexion, redirige vers la page demandée
```

### Déconnexion
```
1. Utilisateur clique sur "Déconnexion"
2. Système détruit la session
3. Affiche un message de confirmation
4. Redirige vers /auth/login/
```

## 🐛 Dépannage

### Problème : Impossible de se connecter

**Solutions** :
1. Vérifier que l'utilisateur existe dans la base de données
2. Vérifier que le mot de passe est correct
3. Vérifier que l'email est correct (sensible à la casse)
4. Vérifier les logs Django pour plus de détails

### Problème : Redirection infinie

**Solution** :
- Vérifier que `LOGIN_URL` et `LOGIN_REDIRECT_URL` sont différents
- Vérifier qu'aucune page protégée n'est définie comme `LOGIN_REDIRECT_URL`

### Problème : Session expire trop vite

**Solution** :
- Cocher "Se souvenir de moi" lors de la connexion
- Vérifier la configuration de `SESSION_COOKIE_AGE` dans settings.py

## 📊 Statistiques de Session

### Durée de Session

- **Sans "Se souvenir de moi"** : Jusqu'à la fermeture du navigateur
- **Avec "Se souvenir de moi"** : 1,209,600 secondes (14 jours)

## 🎯 Bonnes Pratiques

1. **Mots de passe** : Utiliser des mots de passe forts (8+ caractères, majuscules, minuscules, chiffres)
2. **Déconnexion** : Toujours se déconnecter sur un ordinateur partagé
3. **HTTPS** : En production, toujours utiliser HTTPS
4. **Sauvegardes** : Sauvegarder régulièrement la base de données utilisateurs

## 🔗 URLs Disponibles

| URL | Nom | Description |
|-----|-----|-------------|
| `/auth/login/` | `authentication:login` | Page de connexion |
| `/auth/logout/` | `authentication:logout` | Déconnexion |
| `/` | `home` | Redirige vers la page de connexion |

## 📚 Fichiers Importants

```
authentication/
├── forms.py          # LoginForm
├── views.py          # login_view, logout_view
├── urls.py           # URLs d'authentification
├── models.py         # Modèle User personnalisé
└── templates/
    └── authentication/
        └── login.html  # Template de connexion
```

## ✅ Checklist de Vérification

Avant de déployer en production :

- [ ] Changer `SECRET_KEY` dans settings.py
- [ ] Définir `DEBUG = False`
- [ ] Configurer `ALLOWED_HOSTS`
- [ ] Activer HTTPS
- [ ] Configurer les emails (pour réinitialisation de mot de passe)
- [ ] Tester tous les flux d'authentification
- [ ] Vérifier les permissions des utilisateurs

## 🎉 Prêt à Utiliser !

Le système d'authentification est maintenant opérationnel. Les utilisateurs peuvent se connecter et accéder aux fonctionnalités protégées de l'application.
