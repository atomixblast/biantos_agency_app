# 🪟 Guide d'Installation Windows - Biantos Agency

## 🎯 Solutions Proposées

### ✅ **Solution 1 : Application Electron (Recommandée)**
Application de bureau native avec Django en backend

### ✅ **Solution 2 : Installateur Batch Simple**
Script d'installation automatique

### ✅ **Solution 3 : Docker Desktop**
Conteneurisation professionnelle

---

## 📦 Solution 1 : Application Electron (LA MEILLEURE)

### Avantages
- ✅ Vraie application Windows native
- ✅ Icône dans la barre des tâches
- ✅ Pas de console visible
- ✅ Installation simple (un seul .exe)
- ✅ Auto-update possible

### Étapes d'installation

1. **Installer Node.js** : https://nodejs.org/

2. **Créer le wrapper Electron** :

```bash
# Dans le dossier du projet
npm init -y
npm install electron electron-builder
```

3. **Les fichiers seront créés automatiquement** (voir ci-dessous)

4. **Compiler** :
```bash
npm run build
```

5. **L'installateur sera dans** `dist/BiantosAgency-Setup.exe`

---

## 🔧 Solution 2 : Installateur Batch Simple (RAPIDE)

### Avantages
- ✅ Très simple
- ✅ Pas de dépendances externes
- ✅ Installation en 1 clic

### Utilisation

1. **Double-cliquer sur** `install_windows.bat`
2. **Suivre les instructions**
3. **Lancer via** `start_biantos.bat`

---

## 🐳 Solution 3 : Docker Desktop (PROFESSIONNEL)

### Avantages
- ✅ Isolation complète
- ✅ Portable entre machines
- ✅ Facile à mettre à jour

### Installation

1. **Installer Docker Desktop** : https://www.docker.com/products/docker-desktop/

2. **Double-cliquer sur** `start_docker.bat`

3. **L'application démarre automatiquement**

---

## 📊 Comparaison des Solutions

| Critère | Electron | Batch | Docker |
|---------|----------|-------|--------|
| Facilité | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Professionnel | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Taille | ~150 MB | ~50 MB | ~500 MB |
| Performance | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🚀 Démarrage Rapide

### Pour les utilisateurs finaux :

**Méthode Simple (Batch)** :
1. Extraire le ZIP
2. Double-cliquer sur `install_windows.bat`
3. Double-cliquer sur `start_biantos.bat`

**Méthode Professionnelle (Electron)** :
1. Télécharger `BiantosAgency-Setup.exe`
2. Installer
3. Lancer depuis le menu Démarrer

---

## 📝 Notes Importantes

- **Python requis** : Python 3.10+ doit être installé
- **Première utilisation** : Créer un superutilisateur avec `python manage.py createsuperuser`
- **Port** : L'application utilise le port 8000
- **Données** : Stockées dans `db.sqlite3`

---

## 🆘 Support

En cas de problème :
1. Vérifier que Python est installé
2. Vérifier que le port 8000 est libre
3. Consulter les logs dans `logs/`
