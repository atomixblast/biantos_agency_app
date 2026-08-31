"""
Script pour créer un package de distribution Windows
Crée un ZIP prêt à être distribué aux utilisateurs
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# Configuration
APP_NAME = "BiantosAgency"
VERSION = "1.0.0"
OUTPUT_DIR = "distribution"

# Fichiers et dossiers à inclure
INCLUDE_PATTERNS = [
    # Fichiers racine essentiels
    'manage.py',
    'requirements.txt',
    'install_windows.bat',
    
    # Documentation
    'INSTALLATION_WINDOWS.md',
    'BUILD_GUIDE.md',
    
    # Applications Django
    'order/',
    'authentication/',
    'biantos_agency/',
    
    # Templates et static
    'templates/',
    'static/',
    
    # Base de données vide (optionnel)
    # 'db.sqlite3',
]

# Fichiers et dossiers à exclure
EXCLUDE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.Python',
    'venv/',
    'env/',
    '.env',
    '.git/',
    '.gitignore',
    '.vscode/',
    '.idea/',
    'node_modules/',
    'dist/',
    'build/',
    '*.egg-info/',
    '.pytest_cache/',
    'htmlcov/',
    '.coverage',
    'db.sqlite3',  # Ne pas inclure la base de données de dev
    'media/*',  # Ne pas inclure les médias de dev
    '*.log',
    'logs/',
]

def should_exclude(path):
    """Vérifie si un fichier/dossier doit être exclu"""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern.endswith('/'):
            if pattern[:-1] in path_str.split(os.sep):
                return True
        elif pattern.startswith('*.'):
            if path_str.endswith(pattern[1:]):
                return True
        elif pattern in path_str:
            return True
    return False

def create_readme():
    """Crée un README pour l'utilisateur final"""
    readme_content = """╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           🏢 BIANTOS AGENCY v{version}                  ║
║              Gestion de Commandes                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

📖 INSTALLATION RAPIDE
══════════════════════

1️⃣  Extraire ce ZIP dans un dossier de votre choix

2️⃣  Double-cliquer sur : install_windows.bat

3️⃣  Suivre les instructions à l'écran

4️⃣  Lancer l'application avec : start_biantos.bat

═══════════════════════════════════════════════════════════

⚠️  PRÉREQUIS
═════════════

Python 3.10 ou supérieur doit être installé sur votre PC.

📥 Télécharger Python : https://www.python.org/downloads/

⚠️  IMPORTANT : Cochez "Add Python to PATH" lors de l'installation !

═══════════════════════════════════════════════════════════

📁 CONTENU DU PACKAGE
═════════════════════

✓ Application Django complète
✓ Script d'installation automatique
✓ Documentation complète
✓ Tous les fichiers nécessaires

═══════════════════════════════════════════════════════════

🆘 BESOIN D'AIDE ?
═════════════════

Consultez le fichier : INSTALLATION_WINDOWS.md

═══════════════════════════════════════════════════════════

© 2024 Biantos - Version {version}
""".format(version=VERSION)
    
    return readme_content

def create_distribution_zip():
    """Crée le ZIP de distribution"""
    print(f"🚀 Création du package de distribution {APP_NAME} v{VERSION}")
    print("=" * 60)
    
    # Créer le dossier de sortie
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    
    # Nom du fichier ZIP
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_filename = f"{APP_NAME}_v{VERSION}_{timestamp}.zip"
    zip_path = output_path / zip_filename
    
    # Supprimer l'ancien ZIP s'il existe
    if zip_path.exists():
        zip_path.unlink()
        print(f"🗑️  Ancien fichier supprimé")
    
    print(f"\n📦 Création de {zip_filename}...")
    
    # Créer le README
    readme_content = create_readme()
    readme_path = Path("README_INSTALLATION.txt")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Créer le ZIP
    file_count = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Ajouter le README
        zipf.write(readme_path, readme_path.name)
        file_count += 1
        
        # Parcourir tous les fichiers du projet
        for root, dirs, files in os.walk('.'):
            # Filtrer les dossiers à exclure
            dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                
                # Vérifier si le fichier doit être exclu
                if should_exclude(file_path):
                    continue
                
                # Vérifier si le fichier est dans les patterns à inclure
                should_include = False
                for pattern in INCLUDE_PATTERNS:
                    if pattern.endswith('/'):
                        if pattern[:-1] in str(file_path).split(os.sep):
                            should_include = True
                            break
                    elif str(file_path).startswith(pattern) or file == pattern:
                        should_include = True
                        break
                
                if should_include:
                    # Ajouter au ZIP
                    arcname = str(file_path).lstrip('./')
                    zipf.write(file_path, arcname)
                    file_count += 1
                    print(f"  ✓ {arcname}")
    
    # Nettoyer le README temporaire
    readme_path.unlink()
    
    # Statistiques
    zip_size = zip_path.stat().st_size / (1024 * 1024)  # Taille en MB
    
    print("\n" + "=" * 60)
    print(f"✅ Package créé avec succès !")
    print(f"📁 Fichier : {zip_path}")
    print(f"📊 Fichiers inclus : {file_count}")
    print(f"💾 Taille : {zip_size:.2f} MB")
    print("=" * 60)
    
    return zip_path

def create_test_instructions():
    """Crée un guide de test"""
    instructions = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           📋 GUIDE DE TEST - BIANTOS AGENCY             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

🧪 COMMENT TESTER LE PACKAGE
═════════════════════════════

1. PRÉPARATION
   ────────────
   ✓ Extraire le ZIP dans un dossier de test
   ✓ S'assurer que Python 3.10+ est installé
   ✓ Fermer toutes les instances de l'application

2. INSTALLATION
   ────────────
   ✓ Double-cliquer sur install_windows.bat
   ✓ Vérifier qu'il n'y a pas d'erreurs
   ✓ Créer un compte administrateur quand demandé
   ✓ Noter le temps d'installation

3. PREMIER DÉMARRAGE
   ─────────────────
   ✓ Double-cliquer sur start_biantos.bat
   ✓ Vérifier que le navigateur s'ouvre
   ✓ Vérifier l'accès à http://127.0.0.1:8000
   ✓ Se connecter avec le compte créé

4. TESTS FONCTIONNELS
   ──────────────────
   ✓ Créer un article avec photo
   ✓ Créer un client avec photo
   ✓ Créer un apporteur d'affaires avec photo
   ✓ Créer une commande
   ✓ Ajouter un paiement
   ✓ Générer une facture
   ✓ Consulter le calendrier
   ✓ Voir les rapports

5. ARRÊT
   ─────
   ✓ Appuyer sur CTRL+C dans la console
   ✓ OU double-cliquer sur stop_biantos.bat
   ✓ Vérifier que le serveur s'arrête proprement

6. REDÉMARRAGE
   ───────────
   ✓ Relancer avec start_biantos.bat
   ✓ Vérifier que les données sont conservées
   ✓ Vérifier que les photos sont toujours là

7. DÉSINSTALLATION (OPTIONNEL)
   ───────────────────────────
   ✓ Double-cliquer sur uninstall_biantos.bat
   ✓ Vérifier que venv/ est supprimé
   ✓ Vérifier que db.sqlite3 et media/ sont conservés

═══════════════════════════════════════════════════════════

✅ CHECKLIST DE VALIDATION
═══════════════════════════

Installation :
□ Pas d'erreurs pendant l'installation
□ Environnement virtuel créé (venv/)
□ Dépendances installées
□ Base de données créée
□ Fichiers de démarrage générés

Fonctionnement :
□ Serveur démarre sans erreur
□ Navigateur s'ouvre automatiquement
□ Interface accessible
□ Connexion fonctionne
□ Upload de photos fonctionne
□ Création de commandes fonctionne
□ Génération de factures fonctionne

Performance :
□ Temps de démarrage < 10 secondes
□ Interface réactive
□ Pas de lenteur notable

Stabilité :
□ Pas de crash pendant l'utilisation
□ Données conservées après redémarrage
□ Arrêt propre du serveur

═══════════════════════════════════════════════════════════

📝 NOTES DE TEST
════════════════

Date du test : _________________
Testeur : _____________________
Version Windows : ______________
Version Python : _______________

Problèmes rencontrés :
_______________________________
_______________________________
_______________________________

Suggestions d'amélioration :
_______________________________
_______________________________
_______________________________

═══════════════════════════════════════════════════════════
"""
    
    test_file = Path(OUTPUT_DIR) / "GUIDE_TEST.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"\n📋 Guide de test créé : {test_file}")

if __name__ == "__main__":
    try:
        # Créer le ZIP de distribution
        zip_path = create_distribution_zip()
        
        # Créer le guide de test
        create_test_instructions()
        
        print(f"\n🎉 Distribution prête !")
        print(f"\n📦 Fichiers créés dans le dossier '{OUTPUT_DIR}/' :")
        print(f"   • {zip_path.name} - Package de distribution")
        print(f"   • GUIDE_TEST.txt - Guide de test")
        
        print(f"\n💡 Prochaines étapes :")
        print(f"   1. Tester le package sur une machine Windows")
        print(f"   2. Suivre le guide de test")
        print(f"   3. Distribuer le ZIP aux utilisateurs")
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
