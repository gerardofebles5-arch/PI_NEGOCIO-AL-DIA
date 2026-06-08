@echo off
REM Script de automatización silenciosa para (π)NAD V6.0
REM Este script ejecuta todo automáticamente sin pedir confirmación

echo ==========================================
echo (π)NAD V6.0 - Automatización Silenciosa
echo ==========================================
echo.
echo Este script configurará todo automáticamente.
echo Solo requerirá interacción para autenticación.
echo.

REM Crear log
set LOG_FILE=auto_setup_silent.log
echo Iniciando automatización silenciosa > %LOG_FILE%
echo Fecha: %date% %time% >> %LOG_FILE%

REM Paso 1: Crear entorno Python
echo [1/8] Configurando entorno Python...
if not exist venv (
    python -m venv venv >> %LOG_FILE% 2>&1
    echo ✓ Virtual environment creado >> %LOG_FILE%
) else (
    echo ✓ Virtual environment ya existe >> %LOG_FILE%
)

REM Paso 2: Instalar dependencias
echo [2/8] Instalando dependencias de Python...
call venv\Scripts\activate.bat
pip install --upgrade pip >> %LOG_FILE% 2>&1
pip install -r requirements.txt >> %LOG_FILE% 2>&1
echo ✓ Dependencias instaladas >> %LOG_FILE%

REM Paso 3: Crear directorios
echo [3/8] Creando directorios...
if not exist config mkdir config
if not exist logs mkdir logs
if not exist data mkdir data
if not exist data\uploads mkdir data\uploads
if not exist data\exports mkdir data\exports
if not exist data\backups mkdir data\backups
echo ✓ Directorios creados >> %LOG_FILE%

REM Paso 4: Configurar .env
echo [4/8] Configurando .env...
if not exist .env (
    copy .env.example .env
    echo ✓ .env creado >> %LOG_FILE%
) else (
    echo ✓ .env ya existe >> %LOG_FILE%
)

REM Paso 5: Verificar Google Cloud
echo [5/8] Verificando Google Cloud SDK...
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Google Cloud SDK no encontrado >> %LOG_FILE%
    echo.
    echo ==========================================
    echo REQUIERE INTERVENCIÓN MANUAL
    echo ==========================================
    echo.
    echo Google Cloud SDK no está instalado.
    echo Descargando instalador automáticamente...
    echo.
    REM Descargar e instalar Google Cloud SDK automáticamente
    powershell -Command "Invoke-WebRequest -Uri 'https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe' -OutFile 'GoogleCloudSDKInstaller.exe'"
    echo ✓ Instalador descargado
    echo.
    echo Ejecutando instalador...
    start /wait GoogleCloudSDKInstaller.exe
    del GoogleCloudSDKInstaller.exe
    echo.
    echo Google Cloud SDK instalado. Por favor autentícate:
    gcloud auth login
    gcloud config set project pinad-production
    gcloud config set compute/region us-central1
) else (
    echo ✓ Google Cloud SDK encontrado >> %LOG_FILE%
    gcloud version >> %LOG_FILE%
)

REM Paso 6: Verificar Flutter
echo [6/8] Verificando Flutter SDK...
flutter --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Flutter no encontrado >> %LOG_FILE%
    echo.
    echo ==========================================
    echo REQUIERE INTERVENCIÓN MANUAL
    echo ==========================================
    echo.
    echo Flutter no está instalado.
    echo Ejecutando instalación automática...
    call scripts\install_flutter.bat
) else (
    echo ✓ Flutter encontrado >> %LOG_FILE%
    flutter --version >> %LOG_FILE%
)

REM Paso 7: Instalar dependencias de Flutter
echo [7/8] Instalando dependencias de Flutter...
if exist pinad_app (
    cd pinad_app
    flutter pub get >> %LOG_FILE% 2>&1
    cd ..
    echo ✓ Dependencias de Flutter instaladas >> %LOG_FILE%
)

REM Paso 8: Verificar Firebase CLI
echo [8/8] Verificando Firebase CLI...
firebase --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Firebase CLI no encontrado >> %LOG_FILE%
    echo Instalando Firebase CLI...
    npm install -g firebase-tools >> %LOG_FILE% 2>&1
    echo ✓ Firebase CLI instalado >> %LOG_FILE%
) else (
    echo ✓ Firebase CLI encontrado >> %LOG_FILE%
    firebase --version >> %LOG_FILE%
)

echo.
echo ==========================================
echo AUTOMATIZACIÓN COMPLETADA
echo ==========================================
echo.
echo Revisa %LOG_FILE% para detalles.
echo.
echo Componentes instalados:
if exist venv echo ✓ Python virtual environment
if exist .env echo ✓ Archivo .env
gcloud --version >nul 2>&1 && echo ✓ Google Cloud SDK
flutter --version >nul 2>&1 && echo ✓ Flutter SDK
firebase --version >nul 2>&1 && echo ✓ Firebase CLI
echo.
echo ==========================================
echo PRÓXIMOS PASOS (REQUIEREN INTERVENCIÓN MANUAL)
echo ==========================================
echo.
echo 1. Configura Google Cloud:
echo    gcloud auth login
echo    gcloud config set project YOUR_PROJECT_ID
echo    scripts\setup_google_cloud.bat
echo.
echo 2. Configura Firebase:
echo    firebase login
echo    scripts\setup_firebase.bat
echo.
echo 3. Configura .env con tus credenciales:
echo    Abre .env y reemplaza los valores placeholder
echo.
echo 4. Ejecuta el backend:
echo    scripts\run_backend_updated.bat
echo.
echo 5. Ejecuta Flutter:
echo    scripts\run_flutter_updated.bat
echo.
pause
