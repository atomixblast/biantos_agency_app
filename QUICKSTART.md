# 🚀 Guide de Démarrage Rapide - Biantos Agency

## 📋 Prérequis

- Python 3.8+
- Django installé
- Base de données configurée

## 🔧 Installation et Configuration

### 1. Appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Créer un superutilisateur (si pas encore fait)

```bash
python manage.py createsuperuser
```

### 3. Créer des données de test (optionnel)

```bash
python manage.py shell
```

Puis dans le shell Python :

```python
from order.models import Customer, SalesExecutive, Article

# Créer des clients
Customer.objects.create(name="Jean Dupont", tel="0601020304")
Customer.objects.create(name="Marie Martin", tel="0605060708")

# Créer des apporteurs d'affaires
SalesExecutive.objects.create(name="Paul Bernard", tel="0701020304")
SalesExecutive.objects.create(name="Sophie Dubois", tel="0705060708")

# Créer des articles
Article.objects.create(name="Tasse personnalisée", ref="TASSE001", sale_price=5000)
Article.objects.create(name="T-shirt imprimé", ref="TSHIRT001", sale_price=8000)
Article.objects.create(name="Casquette brodée", ref="CAP001", sale_price=3500)
Article.objects.create(name="Mug thermique", ref="MUG001", sale_price=6500)
Article.objects.create(name="Sac personnalisé", ref="SAC001", sale_price=12000)

print("✅ Données de test créées avec succès!")
```

Ou utilisez le script de test si disponible :

```bash
python setup_test_data.py
```

## 🎯 Utilisation

### Démarrer le serveur

```bash
python manage.py runserver
```

### Accéder à l'application

- **Page d'accueil** : http://localhost:8000/
- **Admin Django** : http://localhost:8000/admin/
- **Liste des commandes** : http://localhost:8000/order/list_orders/
- **Créer une commande** : http://localhost:8000/order/create_order/

## 📝 Workflow de Création de Commande

### Étape 1 : Accéder à la création
1. Naviguer vers `/order/create_order/`
2. Ou cliquer sur "Nouvelle commande" depuis la liste

### Étape 2 : Ajouter des articles
1. Cliquer sur "Ajouter un article à la commande"
2. Sélectionner un article dans la liste déroulante
3. Entrer la quantité
4. Entrer la remise (%) si applicable
5. Cliquer sur "Ajouter"
6. Répéter pour tous les articles souhaités

### Étape 3 : Finaliser la commande
1. Vérifier le total calculé automatiquement
2. Cliquer sur "Terminer la commande"
3. Remplir le formulaire :
   - **Désignation** : Nom de la commande
   - **Client** : Sélectionner dans la liste
   - **Apporteur d'affaire** : Sélectionner dans la liste (optionnel)
   - **Date de la commande** : Date de création
   - **Statut** : PENDING, DONE ou CANCELED
   - **Montant encaissé** : Montant déjà payé
   - **Remise** : Remise globale sur la commande
4. Cliquer sur "Enregistrer la commande"

## 🔄 Workflow de Mise à Jour de Commande

### Étape 1 : Accéder à la modification
1. Depuis la liste des commandes, cliquer sur "Modifier"
2. Les articles existants sont automatiquement chargés

### Étape 2 : Modifier les articles
1. **Supprimer** un article : Cliquer sur l'icône de suppression
2. **Ajouter** un article : Même processus que la création
3. Le total est recalculé automatiquement

### Étape 3 : Enregistrer les modifications
1. Cliquer sur "Enregistrer les modifications"
2. Confirmer dans le modal
3. Les modifications sont appliquées

## 🎨 Interface Admin Django

### Accès
1. Naviguer vers `/admin/`
2. Se connecter avec le superutilisateur

### Fonctionnalités disponibles
- ✅ Gestion des **Commandes** (avec articles inline)
- ✅ Gestion des **Clients**
- ✅ Gestion des **Apporteurs d'affaires**
- ✅ Gestion des **Articles**

### Avantages de l'admin
- Recherche avancée
- Filtres par date, statut, client
- Export de données
- Modification en masse

## 🧪 Tests

### Lancer les tests

```bash
# Tous les tests
python manage.py test order

# Tests spécifiques
python manage.py test order.tests.OrderModelTest
python manage.py test order.tests.OrderViewTest
python manage.py test order.tests.ArticleOrderTest

# Avec verbosité
python manage.py test order --verbosity=2
```

### Coverage (si installé)

```bash
coverage run --source='order' manage.py test order
coverage report
coverage html
```

## 🐛 Dépannage

### Problème : Les articles ne s'affichent pas
**Solution** : Vérifier que des articles existent dans la base de données

```bash
python manage.py shell
>>> from order.models import Article
>>> Article.objects.count()
```

### Problème : Erreur 404 sur les URLs
**Solution** : Vérifier que les URLs sont bien incluses dans le fichier principal

Dans `biantos_agency/urls.py` :
```python
urlpatterns = [
    path('order/', include('order.urls')),
    # ...
]
```

### Problème : Les migrations ne s'appliquent pas
**Solution** : 
```bash
python manage.py migrate --run-syncdb
```

### Problème : Erreur de template
**Solution** : Vérifier que Cotton est installé et configuré dans `INSTALLED_APPS`

## 📊 Exemples de Calculs

### Exemple 1 : Commande simple
- Article : Tasse personnalisée (5000 FCFA)
- Quantité : 10
- Remise article : 10%
- **Calcul** : 10 × 5000 × (1 - 0.10) = **45,000 FCFA**

### Exemple 2 : Commande multiple
- Article 1 : T-shirt (8000 FCFA) × 5, remise 15%
  - Sous-total : 5 × 8000 × (1 - 0.15) = 34,000 FCFA
- Article 2 : Casquette (3500 FCFA) × 10, remise 0%
  - Sous-total : 10 × 3500 = 35,000 FCFA
- **Total commande** : 34,000 + 35,000 = **69,000 FCFA**

## 🔐 Sécurité

### Points importants
1. ✅ Les prix sont **toujours recalculés côté serveur**
2. ✅ Impossible de manipuler les prix depuis le navigateur
3. ✅ Protection CSRF activée sur tous les formulaires
4. ✅ Authentification requise pour la liste des commandes

## 📚 Ressources

- **Documentation complète** : Voir `order/README.md`
- **Code source** : `/home/king/biantos_agency/order/`
- **Templates** : `/home/king/biantos_agency/order/templates/`
- **JavaScript** : `/home/king/biantos_agency/order/static/order/js/`

## ✅ Checklist de Vérification

Avant de commencer à utiliser l'application :

- [ ] Migrations appliquées
- [ ] Superutilisateur créé
- [ ] Au moins 1 client créé
- [ ] Au moins 1 article créé
- [ ] Serveur de développement lancé
- [ ] Page de liste des commandes accessible

## 🎉 Prêt à Démarrer !

Votre système de gestion de commandes est maintenant opérationnel. Commencez par créer votre première commande !

```bash
# Démarrer le serveur
python manage.py runserver

# Ouvrir dans le navigateur
# http://localhost:8000/order/create_order/
```

Bonne utilisation ! 🚀
