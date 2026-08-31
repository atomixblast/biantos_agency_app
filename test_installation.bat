@echo off
chcp 65001 >nul
color 0E
title Test Installation Biantos Agency

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║           🧪 TEST D'INSTALLATION - BIANTOS AGENCY       ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Variables de test
set "TEST_PASSED=0"
set "TEST_FAILED=0"

echo 📋 Début des tests...
echo.

:: Test 1 : Python installé
echo [TEST 1] Vérification de Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python est installé
    set /a TEST_PASSED+=1
    python --version
) else (
    echo ❌ Python n'est pas installé
    set /a TEST_FAILED+=1
)
echo.

:: Test 2 : Fichiers requis présents
echo [TEST 2] Vérification des fichiers requis...
set "REQUIRED_FILES=manage.py requirements.txt install_windows.bat"
for %%f in (%REQUIRED_FILES%) do (
    if exist "%%f" (
        echo ✅ %%f trouvé
        set /a TEST_PASSED+=1
    ) else (
        echo ❌ %%f manquant
        set /a TEST_FAILED+=1
    )
)
echo.

:: Test 3 : Dossiers Django présents
echo [TEST 3] Vérification des dossiers Django...
set "REQUIRED_DIRS=order authentication biantos_agency templates"
for %%d in (%REQUIRED_DIRS%) do (
    if exist "%%d\" (
        echo ✅ Dossier %%d trouvé
        set /a TEST_PASSED+=1
    ) else (
        echo ❌ Dossier %%d manquant
        set /a TEST_FAILED+=1
    )
)
echo.

:: Test 4 : Vérifier si l'environnement virtuel existe déjà
echo [TEST 4] Vérification de l'environnement virtuel...
if exist "venv\" (
    echo ℹ️  Environnement virtuel déjà existant
    echo ✅ Test passé
    set /a TEST_PASSED+=1
) else (
    echo ⚠️  Environnement virtuel non créé (normal avant installation)
    echo ✅ Test passé
    set /a TEST_PASSED+=1
)
echo.

:: Test 5 : Vérifier la version de Python
echo [TEST 5] Vérification de la version de Python...
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python 3.10+ détecté
    set /a TEST_PASSED+=1
) else (
    echo ❌ Python 3.10+ requis
    set /a TEST_FAILED+=1
)
echo.

:: Test 6 : Vérifier pip
echo [TEST 6] Vérification de pip...
python -m pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ pip est disponible
    set /a TEST_PASSED+=1
) else (
    echo ❌ pip n'est pas disponible
    set /a TEST_FAILED+=1
)
echo.

:: Test 7 : Vérifier le port 8000
echo [TEST 7] Vérification du port 8000...
netstat -an | find ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Port 8000 déjà utilisé
    echo ℹ️  Arrêtez l'application en cours avant de tester
    set /a TEST_FAILED+=1
) else (
    echo ✅ Port 8000 disponible
    set /a TEST_PASSED+=1
)
echo.

:: Test 8 : Espace disque
echo [TEST 8] Vérification de l'espace disque...
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do set FREE_SPACE=%%a
echo ℹ️  Espace disponible : %FREE_SPACE% octets
echo ✅ Test passé
set /a TEST_PASSED+=1
echo.

:: Résumé des tests
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo 📊 RÉSUMÉ DES TESTS
echo ───────────────────
echo.
echo ✅ Tests réussis : %TEST_PASSED%
echo ❌ Tests échoués : %TEST_FAILED%
echo.

if %TEST_FAILED% equ 0 (
    echo ╔══════════════════════════════════════════════════════════╗
    echo ║                                                          ║
    echo ║           ✅ TOUS LES TESTS SONT PASSÉS !               ║
    echo ║                                                          ║
    echo ╚══════════════════════════════════════════════════════════╝
    echo.
    echo 🎉 Votre système est prêt pour l'installation !
    echo.
    echo 📝 Prochaines étapes :
    echo    1. Exécuter install_windows.bat
    echo    2. Suivre les instructions
    echo    3. Lancer avec start_biantos.bat
    echo.
) else (
    echo ╔══════════════════════════════════════════════════════════╗
    echo ║                                                          ║
    echo ║           ⚠️  CERTAINS TESTS ONT ÉCHOUÉ                ║
    echo ║                                                          ║
    echo ╚══════════════════════════════════════════════════════════╝
    echo.
    echo 🔧 Veuillez corriger les problèmes avant d'installer
    echo.
)

echo ═══════════════════════════════════════════════════════════
echo.

:: Proposer de lancer l'installation
if %TEST_FAILED% equ 0 (
    set /p launch_install="🚀 Voulez-vous lancer l'installation maintenant ? (o/n): "
    if /i "!launch_install!"=="o" (
        echo.
        echo 🚀 Lancement de l'installation...
        call install_windows.bat
    )
)

pause
