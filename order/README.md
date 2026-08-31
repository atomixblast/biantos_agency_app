# Module de Gestion des Commandes - Biantos Agency

## 📋 Vue d'ensemble

Ce module permet de gérer l'ensemble du cycle de vie des commandes, depuis leur création jusqu'à leur mise à jour et suivi.

## 🗂️ Structure des Modèles

### Customer (Client)
- **name** : Nom du client
- **tel** : Numéro de téléphone
- **created_at** / **updated_at** : Horodatage

### SalesExecutive (Apporteur d'affaire)
- **name** : Nom de l'apporteur d'affaire
- **tel** : Numéro de téléphone
- **created_at** / **updated_at** : Horodatage

### Article
- **name** : Nom de l'article/service
- **ref** : Référence unique
- **sale_price** : Prix de vente
- **created_at** / **updated_at** : Horodatage

### Order (Commande)
- **name** : Désignation de la commande
- **state** : Statut (PENDING, DONE, CANCELED)
- **total** : Montant total (calculé automatiquement)
- **discount** : Remise globale
- **cashed** : Montant encaissé
- **ordered_at** : Date de la commande
- **customer** : Client associé
- **sales_executive** : Apporteur d'affaire associé
- **json_repr** : Représentation JSON des articles

### ArticleOrder (Relation Article-Commande)
- **article** : Article concerné
- **order** : Commande concernée
- **qty** : Quantité
- **discount** : Remise spécifique à l'article (en %)

## 🚀 Fonctionnalités

### 1. Liste des commandes
**URL** : `/order/list_orders/`

- Affichage de toutes les commandes
- Filtres par statut, client, apporteur d'affaire
- Recherche par nom
- Export (Excel, CSV, PDF)
- Pagination

### 2. Création de commande
**URL** : `/order/create_order/`

**Processus** :
1. Ajouter des articles avec quantité et remise
2. Le total est calculé automatiquement
3. Remplir le formulaire de commande
4. Validation et enregistrement

**Sécurité** :
- Les prix sont recalculés côté serveur depuis la base de données
- Impossible de manipuler les prix depuis le client

### 3. Mise à jour de commande
**URL** : `/order/update_order/<order_id>/`

**Processus** :
1. Chargement automatique des articles existants
2. Ajout/Suppression d'articles
3. Modification des informations de la commande
4. Validation et enregistrement

**Caractéristiques** :
- Les articles existants sont pré-chargés
- Détection des doublons
- Recalcul automatique des totaux

## 🔧 Administration Django

Accès : `/admin/`

**Modèles enregistrés** :
- ✅ Commandes (avec inline des articles)
- ✅ Clients
- ✅ Apporteurs d'affaires
- ✅ Articles

**Fonctionnalités admin** :
- Recherche avancée
- Filtres personnalisés
- Hiérarchie par date
- Affichage inline des articles de commande

## 📊 Calcul des Totaux

### Pour chaque article :
```
Sous-total = Quantité × Prix unitaire
Remise = Sous-total × (Remise % / 100)
Total article = Sous-total - Remise
```

### Pour la commande :
```
Total commande = Somme(Total de tous les articles)
```

## 🎨 Interface Utilisateur

**Technologies** :
- TailwindCSS pour le style
- Alpine.js pour l'interactivité
- Cotton pour les composants réutilisables

**Composants** :
- `c-order-space` : Interface de création de commande
- `c-order-update-space` : Interface de mise à jour de commande
- `c-order-floating-input` : Champ de saisie flottant
- `c-order-floating-input-article` : Sélecteur d'articles

## 🔒 Sécurité

1. **Validation côté serveur** : Tous les prix sont recalculés depuis la base de données
2. **Protection CSRF** : Tokens CSRF sur tous les formulaires
3. **Authentification** : Décorateur `@login_required` sur les vues
4. **Validation des données** : Utilisation de formulaires Django

## 📝 Workflow Typique

### Création d'une commande :
1. Naviguer vers "Nouvelle commande"
2. Cliquer sur "Ajouter un article"
3. Sélectionner l'article, quantité et remise
4. Répéter pour tous les articles
5. Cliquer sur "Terminer la commande"
6. Remplir les informations (client, apporteur, date, etc.)
7. Enregistrer

### Modification d'une commande :
1. Depuis la liste, cliquer sur "Modifier"
2. Les articles existants sont affichés
3. Ajouter/Supprimer des articles si nécessaire
4. Cliquer sur "Enregistrer les modifications"
5. Confirmer les changements

## 🐛 Débogage

### Problèmes courants :

**Les articles ne s'affichent pas** :
- Vérifier que des articles existent dans la base de données
- Vérifier la console JavaScript pour les erreurs

**Le total ne se calcule pas** :
- Vérifier que Alpine.js est chargé
- Vérifier que les prix des articles sont définis

**Erreur lors de l'enregistrement** :
- Vérifier que tous les champs obligatoires sont remplis
- Vérifier les messages d'erreur Django

## 📦 Dépendances

- Django
- Alpine.js
- TailwindCSS
- django-cotton (pour les composants)

## 🔄 Migrations

Après toute modification des modèles :
```bash
python manage.py makemigrations order
python manage.py migrate
```

## 👥 Contributeurs

Développé pour Biantos Agency
