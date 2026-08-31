# 🏗️ Guide de Construction - Biantos Agency pour Windows

Ce guide détaille les 3 méthodes pour rendre l'application installable sur Windows.

---

## 🎯 Méthode 1 : Installateur Batch (LA PLUS SIMPLE)

### ✅ Avantages
- Aucune dépendance externe
- Installation en 1 clic
- Très rapide
- Facile à distribuer

### 📦 Ce qui est créé
- `install_windows.bat` - Script d'installation
- `start_biantos.bat` - Lance l'application
- `stop_biantos.bat` - Arrête l'application
- `uninstall_biantos.bat` - Désinstalle

### 🚀 Utilisation

**Pour l'utilisateur final** :
1. Copier tout le dossier du projet
2. Double-cliquer sur `install_windows.bat`
3. Suivre les instructions
4. Lancer avec `start_biantos.bat`

**Pour distribuer** :
```bash
# Créer un ZIP avec tous les fichiers
# L'utilisateur extrait et lance install_windows.bat
```

---

## 🖥️ Méthode 2 : Application Electron (LA PLUS PROFESSIONNELLE)

### ✅ Avantages
- Vraie application Windows native
- Un seul fichier .exe à distribuer
- Interface professionnelle
- Pas de console visible
- Icône dans la barre des tâches

### 📦 Prérequis
- Node.js installé : https://nodejs.org/

### 🔨 Construction

```bash
# 1. Installer les dépendances Node.js
npm install

# 2. Construire l'application
npm run build:win

# 3. L'installateur sera dans dist/
# Fichier : BiantosAgency-Setup-1.0.0.exe
```

### 📝 Personnalisation

**Changer l'icône** :
- Remplacer `electron/icon.ico` par votre icône
- Format : .ico, 256x256px recommandé

**Modifier les informations** :
- Éditer `package.json` :
  ```json
  {
    "name": "votre-nom",
    "version": "1.0.0",
    "description": "Votre description"
  }
  ```

**Changer le port** :
- Éditer `electron/main.js` :
  ```javascript
  const DJANGO_PORT = 8000; // Changer ici
  ```

### 🎨 Écran de chargement
- Modifier `electron/loading.html` pour personnaliser

---

## 🐳 Méthode 3 : Docker (LA PLUS PORTABLE)

### ✅ Avantages
- Isolation complète
- Fonctionne partout (Windows, Mac, Linux)
- Facile à mettre à jour
- Professionnel

### 📦 Prérequis
- Docker Desktop : https://www.docker.com/products/docker-desktop/

### 🚀 Utilisation

**Démarrage simple** :
```bash
# Double-cliquer sur start_docker.bat
# OU en ligne de commande :
docker-compose up -d
```

**Arrêt** :
```bash
docker-compose stop
```

**Voir les logs** :
```bash
docker-compose logs -f
```

**Supprimer** :
```bash
docker-compose down
```

### 🔧 Configuration

**Variables d'environnement** :
Créer un fichier `.env` :
```env
DEBUG=False
SECRET_KEY=votre-secret-key
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=admin123
DJANGO_SUPERUSER_EMAIL=admin@example.com
```

---

## 📊 Comparaison des Méthodes

| Critère | Batch | Electron | Docker |
|---------|-------|----------|--------|
| **Facilité d'installation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Apparence professionnelle** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Taille finale** | ~50 MB | ~150 MB | ~500 MB |
| **Portabilité** | Windows | Windows | Tous OS |
| **Mise à jour** | Manuelle | Auto-update possible | Très facile |
| **Isolation** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 Recommandations

### Pour un usage interne (entreprise)
➡️ **Méthode 1 (Batch)** - Simple et efficace

### Pour distribuer à des clients
➡️ **Méthode 2 (Electron)** - Professionnel et élégant

### Pour un environnement de production
➡️ **Méthode 3 (Docker)** - Robuste et portable

---

## 📝 Checklist Avant Distribution

- [ ] Tester sur une machine Windows vierge
- [ ] Vérifier que Python 3.10+ est requis (Batch) ou inclus (Electron)
- [ ] Créer un README pour l'utilisateur final
- [ ] Tester l'installation complète
- [ ] Vérifier les migrations de base de données
- [ ] Tester la création de superutilisateur
- [ ] Vérifier l'upload de fichiers (media/)
- [ ] Tester sur Windows 10 et Windows 11
- [ ] Créer une documentation utilisateur
- [ ] Préparer un guide de dépannage

---

## 🆘 Dépannage Commun

### Erreur "Python not found"
**Solution** : Installer Python 3.10+ depuis python.org

### Erreur "Port 8000 already in use"
**Solution** : Changer le port dans les fichiers de configuration

### Erreur "Permission denied"
**Solution** : Exécuter en tant qu'administrateur

### Docker ne démarre pas
**Solution** : Vérifier que Docker Desktop est bien lancé

---

## 📚 Ressources

- **Python** : https://www.python.org/downloads/
- **Node.js** : https://nodejs.org/
- **Docker Desktop** : https://www.docker.com/products/docker-desktop/
- **Electron** : https://www.electronjs.org/
- **Django Deployment** : https://docs.djangoproject.com/en/stable/howto/deployment/

---

## 🎉 Prochaines Étapes

1. **Choisir votre méthode** selon vos besoins
2. **Tester localement** avant de distribuer
3. **Créer la documentation utilisateur**
4. **Distribuer** à vos utilisateurs

**Bon déploiement ! 🚀**
