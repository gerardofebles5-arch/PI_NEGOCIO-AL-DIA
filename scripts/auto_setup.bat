@echo off
REM Script maestro de automatización para (π)NAD V6.0
REM Este script automatiza todo el proceso de configuración y despliegue

echo ==========================================
echo (π)NAD V6.0 - Automatización Completa
echo ==========================================
echo.

REM Crear log
set LOG_FILE=auto_setup.log
echo Iniciando automatización completa > %LOG_FILE%
echo Fecha: %date% %time% >> %LOG_FILE%

REM Paso 1: Verificar y crear entorno Python
echo [1/10] Verificando entorno Python...
if not exist venv (
    echo Creando virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear virtual environment
        echo Asegúrate de tener Python 3.11+ instalado
        pause
        exit /b 1
    )
    echo ✓ Virtual environment creado >> %LOG_FILE%
) else (
    echo ✓ Virtual environment ya existe
)

REM Paso 2: Instalar dependencias de Python
echo [2/10] Instalando dependencias de Python...
call venv\Scripts\activate.bat
pip install --upgrade pip >> %LOG_FILE% 2>&1
pip install -r requirements.txt >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo WARNING: Algunas dependencias fallaron (requieren dependencias adicionales)
    echo Esto es normal para módulos opcionales
) else (
    echo ✓ Dependencias instaladas >> %LOG_FILE%
)

REM Paso 3: Crear directorios necesarios
echo [3/10] Creando directorios...
if not exist config mkdir config
if not exist logs mkdir logs
if not exist data mkdir data
if not exist data\uploads mkdir data\uploads
if not exist data\exports mkdir data\exports
if not exist data\backups mkdir data\backups
echo ✓ Directorios creados >> %LOG_FILE%

REM Paso 4: Configurar .env
echo [4/10] Configurando variables de entorno...
if not exist .env (
    copy .env.example .env
    echo ✓ .env creado desde .env.example >> %LOG_FILE%
    echo IMPORTANTE: Debes editar .env con tus credenciales reales
) else (
    echo ✓ .env ya existe
)

REM Paso 5: Verificar Google Cloud SDK
echo [5/10] Verificando Google Cloud SDK...
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Google Cloud SDK no encontrado
    echo Descargando e instalando Google Cloud SDK...
    echo NOTA: Esto requiere intervención manual para completar la instalación
    echo Visita: https://cloud.google.com/sdk/docs/install
    echo.
    echo ¿Deseas continuar con la instalación manual? (S/N)
    choice /C SN /N
    if errorlevel 2 (
        echo Saltando Google Cloud SDK
    ) else (
        start https://cloud.google.com/sdk/docs/install
        echo Abre el enlace para instalar Google Cloud SDK
        pause
    )
) else (
    echo ✓ Google Cloud SDK encontrado >> %LOG_FILE%
    gcloud version >> %LOG_FILE%
)

REM Paso 6: Verificar Flutter
echo [6/10] Verificando Flutter SDK...
flutter --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Flutter no encontrado
    echo Ejecutando script de instalación automática de Flutter...
    call scripts\install_flutter.bat
) else (
    echo ✓ Flutter encontrado >> %LOG_FILE%
    flutter --version >> %LOG_FILE%
)

REM Paso 7: Instalar dependencias de Flutter
echo [7/10] Instalando dependencias de Flutter...
if exist pinad_app (
    cd pinad_app
    flutter pub get >> %LOG_FILE% 2>&1
    cd ..
    echo ✓ Dependencias de Flutter instaladas >> %LOG_FILE%
) else (
    echo ✗ Directorio pinad_app no encontrado
)

REM Paso 8: Verificar Terraform
echo [8/10] Verificando Terraform...
terraform --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Terraform no encontrado
    echo Visita: https://learn.hashicorp.com/tutorials/terraform/install-cli
    start https://learn.hashicorp.com/tutorials/terraform/install-cli
    echo Instala Terraform manualmente
) else (
    echo ✓ Terraform encontrado >> %LOG_FILE%
    terraform --version >> %LOG_FILE%
)

REM Paso 9: Verificar Firebase CLI
echo [9/10] Verificando Firebase CLI...
firebase --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Firebase CLI no encontrado
    echo Instalando Firebase CLI...
    npm install -g firebase-tools >> %LOG_FILE% 2>&1
    if errorlevel 1 (
        echo ERROR: No se pudo instalar Firebase CLI
        echo Asegúrate de tener Node.js y npm instalados
    ) else (
        echo ✓ Firebase CLI instalado >> %LOG_FILE%
    )
) else (
    echo ✓ Firebase CLI encontrado >> %LOG_FILE%
    firebase --version >> %LOG_FILE%
)

REM Paso 10: Resumen y siguientes pasos
echo [10/10] Generando resumen...
echo.
echo ==========================================
echo RESUMEN DE AUTOMATIZACIÓN
echo ==========================================
echo.
echo Archivo de log: %LOG_FILE%
echo.
echo Estado de componentes:
if exist venv echo ✓ Python virtual environment
if exist .env echo ✓ Archivo .env
if exist config echo ✓ Directorio config
if exist logs echo ✓ Directorio logs
if exist data echo ✓ Directorio data
gcloud --version >nul 2>&1 && echo ✓ Google Cloud SDK || echo ✗ Google Cloud SDK (requiere instalación manual)
flutter --version >nul 2>&1 && echo ✓ Flutter SDK || echo ✗ Flutter SDK (requiere instalación manual)
terraform --version >nul 2>&1 && echo ✓ Terraform || echo ✗ Terraform (requiere instalación manual)
firebase --version >nul 2>&1 && echo ✓ Firebase CLI || echo ✗ Firebase CLI
echo.
echo ==========================================
echo SIGUIENTES PASOS MANUALES
echo ==========================================
echo.
echo 1. Si Google Cloud SDK no está instalado:
echo    - Instálalo desde: https://cloud.google.com/sdk/docs/install
echo    - Ejecuta: gcloud auth login
echo    - Ejecuta: gcloud config set project YOUR_PROJECT_ID
echo.
echo 2. Si Flutter no está instalado:
echo    - El script de instalación se ejecutará automáticamente
echo    - O instálalo manualmente desde: https://flutter.dev/docs/get-started/install/windows
echo.
echo 3. Configura tus credenciales en .env:
echo    - Abre .env con un editor de texto
echo    - Reemplaza los valores placeholder con tus credenciales reales
echo    - Necesitas: Google Cloud Project ID, Firebase Project ID, etc.
echo.
echo 4. Para configurar Google Cloud automáticamente:
echo    - Ejecuta: scripts\setup_google_cloud.bat (después de instalar gcloud)
echo.
echo 5. Para configurar Firebase automáticamente:
echo    - Ejecuta: scripts\setup_firebase.bat (después de instalar firebase-tools)
echo.
echo 6. Para desplegar infraestructura con Terraform:
echo    - Ejecuta: scripts\deploy_terraform.bat (después de instalar terraform)
echo.
echo 7. Para ejecutar el backend:
echo    - Ejecuta: scripts\run_backend.bat
echo.
echo 8. Para ejecutar la app Flutter:
echo    - Ejecuta: scripts\run_flutter.bat
echo.
echo ==========================================
echo ¿Deseas ejecutar el backend ahora? (S/N)
choice /C SN /N
if errorlevel 2 (
    echo No ejecutando backend
) else (
    echo Ejecutando backend...
    call scripts\run_backend.bat
)

echo.
echo Automatización completada. Revisa %LOG_FILE% para detalles.
pause
