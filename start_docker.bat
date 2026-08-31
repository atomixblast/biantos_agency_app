@echo off
chcp 65001 >nul
color 0B
title Biantos Agency - Docker

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║           🐳 BIANTOS AGENCY - Docker                    ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Vérifier si Docker est installé
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker n'est pas installé !
    echo.
    echo 📥 Téléchargez Docker Desktop depuis :
    echo    https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo ✅ Docker détecté
echo.

:: Vérifier si Docker est en cours d'exécution
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Docker n'est pas démarré !
    echo 🚀 Démarrage de Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo ⏳ Attente du démarrage de Docker...
    timeout /t 10 >nul
)

echo 🔨 Construction de l'image Docker...
docker-compose build

if %errorlevel% neq 0 (
    echo ❌ Erreur lors de la construction
    pause
    exit /b 1
)

echo ✅ Image construite
echo.

echo 🚀 Démarrage du conteneur...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Erreur lors du démarrage
    pause
    exit /b 1
)

echo ✅ Conteneur démarré
echo.

:: Attendre que le serveur soit prêt
echo ⏳ Attente du serveur...
timeout /t 5 >nul

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║           ✅ APPLICATION DÉMARRÉE !                     ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 🌐 Accédez à l'application : http://localhost:8000
echo.
echo 📝 Commandes utiles :
echo    - Voir les logs     : docker-compose logs -f
echo    - Arrêter           : docker-compose stop
echo    - Redémarrer        : docker-compose restart
echo    - Supprimer         : docker-compose down
echo.

:: Ouvrir le navigateur
start http://localhost:8000

echo 💡 Appuyez sur une touche pour voir les logs...
pause >nul

docker-compose logs -f
