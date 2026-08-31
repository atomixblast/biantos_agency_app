# 📊 Guide du Système de Bilan des Commandes

## 🎯 Vue d'Ensemble

Page complète de bilan et d'analyse des commandes avec filtres avancés, statistiques détaillées et export PDF/impression.

---

## ✨ Fonctionnalités Principales

### 1. **Filtres Avancés** 🔍

#### **Filtres Disponibles**
- **📅 Période** : Date de début et date de fin
- **👤 Client** : Sélection d'un client spécifique
- **💼 Apporteur d'affaire** : Filtrage par sales executive
- **📦 Articles** : Multi-sélection (Ctrl+clic pour plusieurs)
- **📋 Statut de commande** : En cours / Fait / Annulé
- **💰 Statut de paiement** : Payé / Partiel / Non payé

#### **Comment Utiliser**
1. Sélectionner les critères souhaités
2. Cliquer sur "Appliquer les filtres"
3. Cliquer sur "Réinitialiser" pour tout effacer

---

### 2. **Statistiques Principales** 💰

#### **4 Cartes de Statistiques**

**📦 Total des Commandes**
- Nombre total de commandes filtrées
- Icône bleue

**💵 Montant Total**
- Somme de toutes les commandes
- Icône violette
- Format : XXX,XXX FCFA

**✅ Total Encaissé**
- Montant déjà payé
- Icône verte
- Format : XXX,XXX FCFA

**⚠️ Reste à Encaisser**
- Montant manquant
- Icône rouge
- Format : XXX,XXX FCFA

---

### 3. **Statistiques Détaillées** 📈

#### **Statuts de Paiement**
- **Commandes payées** : Nombre et pourcentage (vert)
- **Paiements partiels** : Nombre et pourcentage (orange)
- **Non payées** : Nombre et pourcentage (gris)
- **Total remises** : Somme des remises accordées (orange)

#### **Statuts de Commande**
- **Terminées** : Commandes avec statut DONE (teal)
- **En cours** : Commandes avec statut PENDING (jaune)
- **Annulées** : Commandes avec statut CANCELLED (rouge)
- **Taux de paiement** : Pourcentage du montant encaissé

---

### 4. **Liste Détaillée des Commandes** 📋

#### **Colonnes du Tableau**
1. **Commande** : Nom de la commande
2. **Client** : Nom du client
3. **Apporteur** : Nom du sales executive
4. **Total** : Montant total (noir)
5. **Encaissé** : Montant payé (vert)
6. **Reste** : Montant manquant (rouge)
7. **Statut** : 2 badges (commande + paiement)
8. **Date** : Date de création

#### **Badges de Statut**
- **Commande** :
  - 🟢 Fait (teal)
  - 🟡 En cours (jaune)
  - 🔴 Annulé (rouge)
- **Paiement** :
  - 🟢 Payé (vert)
  - 🟠 Partiel (orange)
  - ⚪ Non payé (gris)

---

### 5. **Export et Impression** 🖨️

#### **Bouton Imprimer**
- Ouvre la boîte de dialogue d'impression du navigateur
- Permet de sauvegarder en PDF
- Optimisé pour l'impression :
  - Masque les filtres et boutons
  - Conserve les couleurs des badges
  - Évite les sauts de page dans les éléments

#### **Comment Exporter en PDF**
1. Cliquer sur "Imprimer"
2. Dans la boîte de dialogue :
   - Sélectionner "Enregistrer au format PDF"
   - Ou "Microsoft Print to PDF"
3. Choisir l'emplacement
4. Enregistrer

---

## 🎨 Design et Interface

### **Couleurs Sémantiques**
- **Bleu** : Information générale
- **Violet** : Montants totaux
- **Vert** : Paiements/succès
- **Rouge** : Manquant/erreur
- **Orange** : Partiel/remise
- **Teal** : Terminé
- **Jaune** : En cours
- **Gris** : Non payé/neutre

### **Responsive**
- ✅ Mobile : 1 colonne
- ✅ Tablet : 2 colonnes
- ✅ Desktop : 3-4 colonnes
- ✅ Tableau scrollable horizontalement

### **Dark Mode**
- ✅ Compatible avec le thème sombre
- ✅ Couleurs adaptées automatiquement

---

## 📊 Exemples d'Utilisation

### **Exemple 1 : Bilan Mensuel**
**Objectif** : Voir les performances du mois de janvier

1. **Filtres** :
   - Date début : 01/01/2025
   - Date fin : 31/01/2025
2. **Résultats** :
   - Total commandes : 45
   - Montant total : 2,500,000 FCFA
   - Encaissé : 1,800,000 FCFA
   - Reste : 700,000 FCFA
   - Taux paiement : 72%

### **Exemple 2 : Performance d'un Apporteur**
**Objectif** : Analyser les ventes d'un apporteur d'affaire

1. **Filtres** :
   - Apporteur : Jean Dupont
   - Période : Tout
2. **Résultats** :
   - Total commandes : 23
   - Montant total : 1,200,000 FCFA
   - Commandes payées : 15
   - Paiements partiels : 5
   - Non payées : 3

### **Exemple 3 : Suivi d'un Client**
**Objectif** : Voir l'historique d'un client

1. **Filtres** :
   - Client : Entreprise ABC
2. **Résultats** :
   - Liste de toutes ses commandes
   - Total dépensé
   - Montant restant à payer

### **Exemple 4 : Analyse par Article**
**Objectif** : Voir les commandes contenant un article spécifique

1. **Filtres** :
   - Articles : Article X (Ctrl+clic pour plusieurs)
2. **Résultats** :
   - Commandes contenant cet article
   - Volume total vendu

---

## 🔧 Fonctionnement Technique

### **Vue Django** : `report_orders`
```python
# Filtrage dynamique
- Par période (created_at)
- Par client (customer_id)
- Par apporteur (sales_executive_id)
- Par articles (articles__id__in)
- Par statut commande (state)
- Par statut paiement (méthodes du modèle)

# Calculs
- total_orders = len(orders)
- total_amount = sum(order.total)
- total_paid = sum(order.get_total_paid())
- total_remaining = sum(order.get_remaining_amount())
- total_discount = sum(order.discount)
```

### **URL** : `/order/report/`

### **Template** : `order/report.html`
- Filtres en haut
- 4 cartes de stats principales
- 2 sections de stats détaillées
- Tableau des commandes

---

## 💡 Conseils d'Utilisation

### **Pour un Bilan Rapide**
1. Ne pas appliquer de filtres
2. Voir les statistiques globales
3. Exporter en PDF si besoin

### **Pour une Analyse Ciblée**
1. Combiner plusieurs filtres
2. Exemple : Client + Période
3. Analyser les résultats détaillés

### **Pour un Rapport Mensuel**
1. Filtrer par mois (début + fin)
2. Imprimer ou exporter en PDF
3. Archiver le rapport

### **Pour Suivre les Impayés**
1. Filtrer par "Non payé" ou "Partiel"
2. Voir la liste des commandes
3. Contacter les clients concernés

---

## 📈 Statistiques Calculées

### **Automatiques**
- ✅ Nombre total de commandes
- ✅ Montant total
- ✅ Total encaissé
- ✅ Reste à encaisser
- ✅ Total des remises
- ✅ Répartition par statut
- ✅ Taux de paiement

### **Par Commande**
- ✅ Total
- ✅ Encaissé
- ✅ Reste
- ✅ Statut commande
- ✅ Statut paiement

---

## 🚀 Accès Rapide

### **Depuis la Liste des Commandes**
- Bouton "Bilan" en haut à droite
- Icône graphique 📊

### **URL Directe**
- `/order/report/`

### **Navigation**
- Retour à la liste : Bouton en haut à droite

---

## ✅ Checklist de Vérification

Avant utilisation en production :

- [x] Vue `report_orders` créée
- [x] URL configurée
- [x] Template créé
- [x] Filtres fonctionnels
- [x] Statistiques calculées
- [x] Liste des commandes affichée
- [x] Bouton Bilan dans la navigation
- [x] Fonction d'impression
- [x] Styles d'impression optimisés
- [x] Responsive design
- [x] Dark mode compatible

---

## 🎉 Prêt à Utiliser !

Le système de bilan des commandes est maintenant **100% opérationnel** !

**Fonctionnalités clés** :
- ✅ Filtres avancés (6 critères)
- ✅ Statistiques complètes
- ✅ Liste détaillée
- ✅ Export PDF/Impression
- ✅ Design moderne
- ✅ Responsive
- ✅ Dark mode

**Accès** : `/order/report/` ou bouton "Bilan" dans la liste

**Bon travail ! 📊**
