@echo off
REM Script de configuración con un solo clic
REM Este intenta hacer todo automáticamente con mínima interacción

echo ==========================================
echo (π)NAD V6.0 - Configuración con Un Clic
echo ==========================================
echo.
echo Este script configurará todo automáticamente.
echo Solo necesitarás autenticarte con Google Cloud y Firebase.
echo.

REM Crear directorio de logs
if not exist logs mkdir logs

REM Ejecutar setup silencioso
call scripts\auto_setup_silent.bat

REM Si Google Cloud está instalado, intentar configurar automáticamente
gcloud --version >nul 2>&1
if not errorlevel 1 (
    echo.
    echo ==========================================
    echo Configurando Google Cloud automáticamente
    echo ==========================================
    echo.
    echo Necesitas autenticarte con Google Cloud.
    echo Se abrirá una ventana del navegador.
    echo.
    gcloud auth login
    echo.
    
    REM Configurar proyecto automáticamente
    set PROJECT_ID=pinad-production
    gcloud config set project %PROJECT_ID%
    gcloud config set compute/region us-central1
    gcloud config set compute/zone us-central1-a
    
    echo ✓ Google Cloud configurado
    echo.
    
    REM Ejecutar script de configuración de Google Cloud
    call scripts\setup_google_cloud.bat
)

REM Si Firebase está instalado, intentar configurar automáticamente
firebase --version >nul 2>&1
if not errorlevel 1 (
    echo.
    echo ==========================================
    echo Configurando Firebase automáticamente
    echo ==========================================
    echo.
    echo Necesitas autenticarte con Firebase.
    echo Se abrirá una ventana del navegador.
    echo.
    firebase login
    echo.
    
    REM Ejecutar script de configuración de Firebase
    call scripts\setup_firebase.bat
)

echo.
echo ==========================================
echo CONFIGURACIÓN COMPLETADA
echo ==========================================
echo.
echo Ahora puedes ejecutar:
echo - Backend: scripts\run_backend_updated.bat
echo - Flutter: scripts\run_flutter_updated.bat
echo.
pause
