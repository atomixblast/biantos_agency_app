@echo off
chcp 65001 >nul
color 0A
title Installation Biantos Agency

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║           🏢 BIANTOS AGENCY - Installation              ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé !
    echo.
    echo 📥 Téléchargez Python depuis : https://www.python.org/downloads/
    echo ⚠️  Cochez "Add Python to PATH" lors de l'installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python détecté
echo.

:: Créer l'environnement virtuel
echo 📦 Création de l'environnement virtuel...
if not exist "venv" (
    python -m venv venv
    echo ✅ Environnement virtuel créé
) else (
    echo ℹ️  Environnement virtuel déjà existant
)
echo.

:: Activer l'environnement virtuel
echo 🔄 Activation de l'environnement...
call venv\Scripts\activate.bat

:: Installer les dépendances
echo 📚 Installation des dépendances...
echo ⏳ Cela peut prendre quelques minutes...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)

echo ✅ Dépendances installées
echo.

:: Créer les migrations
echo 🗄️  Configuration de la base de données...
python manage.py makemigrations --noinput
python manage.py migrate --noinput
echo ✅ Base de données configurée
echo.

:: Collecter les fichiers statiques
echo 📦 Collecte des fichiers statiques...
python manage.py collectstatic --noinput --clear >nul 2>&1
echo ✅ Fichiers statiques collectés
echo.

:: Créer le dossier media
if not exist "media" mkdir media
if not exist "media\articles" mkdir media\articles
if not exist "media\customers" mkdir media\customers
if not exist "media\sales_executives" mkdir media\sales_executives

:: Demander si l'utilisateur veut créer un superutilisateur
echo.
echo ═══════════════════════════════════════════════════════════
echo.
set /p create_super="🔐 Voulez-vous créer un compte administrateur ? (o/n): "

if /i "%create_super%"=="o" (
    echo.
    echo 👤 Création du compte administrateur...
    echo.
    python manage.py createsuperuser
)

:: Créer le fichier de démarrage
echo.
echo 📝 Création du raccourci de démarrage...
(
echo @echo off
echo chcp 65001 ^>nul
echo color 0B
echo title Biantos Agency - Serveur
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo  ║                                                         ║
echo ║           🏢 BIANTOS AGENCY - Démarrage                 ║
echo  ║                                                         ║
echo ╚══════════════════════════════════════════════════════════╝ 
echo.
echo 🚀 Démarrage du serveur...
echo 🌐 L'application sera accessible sur http://127.0.0.1:8000
echo.
echo ⏹️  Appuyez sur CTRL+C pour arrêter le serveur
echo.
echo.
call venv\Scripts\activate.bat
start http://127.0.0.1:8000
python manage.py runserver 127.0.0.1:8000
) > start_biantos.bat

echo ✅ Raccourci créé : start_biantos.bat
echo.

:: Créer un raccourci pour arrêter le serveur
(
echo @echo off
echo taskkill /F /IM python.exe /T ^>nul 2^>^&1
echo echo ✅ Serveur arrêté
echo timeout /t 2 ^>nul
) > stop_biantos.bat

echo ✅ Raccourci d'arrêt créé : stop_biantos.bat
echo.

:: Créer un fichier de désinstallation
(
echo @echo off
echo color 0C
echo title Désinstallation Biantos Agency
echo.
echo ⚠️  ATTENTION : Cela supprimera l'environnement virtuel
echo ⚠️  Vos données ^(db.sqlite3, media^) seront conservées
echo.
set /p confirm="Voulez-vous continuer ? (o/n): "
if /i "%%confirm%%"=="o" (
    echo.
    echo 🗑️  Suppression de l'environnement virtuel...
    rmdir /s /q venv
    echo ✅ Désinstallation terminée
    echo.
    echo ℹ️  Pour réinstaller, exécutez install_windows.bat
) else (
    echo ❌ Désinstallation annulée
)
echo.
pause
) > uninstall_biantos.bat

echo ✅ Script de désinstallation créé : uninstall_biantos.bat
echo.

:: Installation terminée
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║           ✅ INSTALLATION TERMINÉE !                    ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 🎉 Biantos Agency est maintenant installé !
echo.
echo 📝 Pour démarrer l'application :
echo    Double-cliquez sur : start_biantos.bat
echo.
echo 🛑 Pour arrêter l'application :
echo    Double-cliquez sur : stop_biantos.bat
echo.
echo 🗑️  Pour désinstaller :
echo    Double-cliquez sur : uninstall_biantos.bat
echo.
echo 💡 Conseil : Créez un raccourci de start_biantos.bat sur le bureau
echo.

set /p start_now="🚀 Voulez-vous démarrer l'application maintenant ? (o/n): "

if /i "%start_now%"=="o" (
    echo.
    echo 🚀 Démarrage de Biantos Agency...
    start start_biantos.bat
) else (
    echo.
    echo 👋 À bientôt !
)

echo.
pause
