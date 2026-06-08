@echo off
REM Script de configuración automática de Google Cloud para Windows

echo ==========================================
echo Configuración Automática de Google Cloud
echo ==========================================
echo.

REM Verificar si gcloud está instalado
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Google Cloud SDK no está instalado
    echo Por favor instálalo primero desde:
    echo https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

echo ✓ Google Cloud SDK encontrado
echo.

REM Login en Google Cloud
echo [1/5] Autenticando con Google Cloud...
gcloud auth login
if errorlevel 1 (
    echo ERROR: No se pudo autenticar con Google Cloud
    pause
    exit /b 1
)
echo ✓ Autenticación completada
echo.

REM Configurar proyecto
echo [2/5] Configurando proyecto de Google Cloud...
set /p PROJECT_ID="Ingresa tu Google Cloud Project ID (o presiona Enter para usar 'pinad-production'): "
if "%PROJECT_ID%"=="" set PROJECT_ID=pinad-production

gcloud config set project %PROJECT_ID%
if errorlevel 1 (
    echo ERROR: No se pudo configurar el proyecto
    pause
    exit /b 1
)
echo ✓ Proyecto configurado: %PROJECT_ID%
echo.

REM Configurar región
echo [3/5] Configurando región...
set /p REGION="Ingresa tu región (o presiona Enter para usar 'us-central1'): "
if "%REGION%"=="" set REGION=us-central1

gcloud config set compute/region %REGION%
gcloud config set compute/zone %REGION%-a
echo ✓ Región configurada: %REGION%
echo.

REM Habilitar APIs requeridas
echo [4/5] Habilitando APIs de Google Cloud...
echo Esto puede tomar varios minutos...
gcloud services enable \
    cloudresourcemanager.googleapis.com \
    compute.googleapis.com \
    storage.googleapis.com \
    sqladmin.googleapis.com \
    bigquery.googleapis.com \
    documentai.googleapis.com \
    aiplatform.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    apigateway.googleapis.com \
    secretmanager.googleapis.com \
    cloudkms.googleapis.com \
    pubsub.googleapis.com \
    scheduler.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    cloudaudit.googleapis.com \
    appengine.googleapis.com

if errorlevel 1 (
    echo WARNING: Algunas APIs podrían no haberse habilitado
    echo Revisa manualmente en: https://console.cloud.google.com/apis/library
) else (
    echo ✓ APIs habilitadas
)
echo.

REM Crear Service Account
echo [5/5] Creando Service Account...
set SA_NAME=pinad-service-account
set SA_EMAIL=%SA_NAME%@%PROJECT_ID%.iam.gserviceaccount.com

gcloud iam service-accounts create %SA_NAME% \
    --display-name="PINAD Service Account" \
    --description="Service account for (π)NAD application"

if errorlevel 1 (
    echo WARNING: No se pudo crear el Service Account
    echo Puede que ya exista
) else (
    echo ✓ Service Account creado: %SA_EMAIL%
)
echo.

REM Asignar roles
echo Asignando roles al Service Account...
gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/editor"

gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/documentai.admin"

gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/aiplatform.admin"

gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/cloudfunctions.admin"

gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/secretmanager.admin"

gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/cloudkms.admin"

gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/pubsub.admin"

gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/monitoring.admin"

gcloud projects add-iam-policy-binding %PROJECT_ID% \
    --member="serviceAccount:%SA_EMAIL%" \
    --role="roles/logging.admin"

echo ✓ Roles asignados
echo.

REM Crear clave del Service Account
echo Creando clave del Service Account...
if not exist config mkdir config
gcloud iam service-accounts keys create config/service_account.json \
    --iam-account=%SA_EMAIL%

if errorlevel 1 (
    echo ERROR: No se pudo crear la clave del Service Account
    pause
    exit /b 1
)

echo ✓ Clave creada: config/service_account.json
echo.

REM Crear buckets
echo Creando buckets de Cloud Storage...
gsutil mb -p %PROJECT_ID% -l %REGION% gs://%PROJECT_ID%-documents
gsutil mb -p %PROJECT_ID% -l %REGION% gs://%PROJECT_ID%-exports
gsutil mb -p %PROJECT_ID% -l %REGION% gs://%PROJECT_ID%-backups

echo ✓ Buckets creados
echo.

REM Actualizar .env
echo Actualizando archivo .env...
if exist .env (
    echo GOOGLE_CLOUD_PROJECT=%PROJECT_ID% >> .env
    echo GOOGLE_CLOUD_REGION=%REGION% >> .env
    echo SERVICE_ACCOUNT_EMAIL=%SA_EMAIL% >> .env
    echo GOOGLE_APPLICATION_CREDENTIALS=config/service_account.json >> .env
    echo ✓ .env actualizado
) else (
    echo WARNING: .env no encontrado
    echo Crea .env desde .env.example primero
)
echo.

echo ==========================================
echo Configuración de Google Cloud completada
echo ==========================================
echo.
echo Proyecto: %PROJECT_ID%
echo Región: %REGION%
echo Service Account: %SA_EMAIL%
echo.
echo Archivo de credenciales: config/service_account.json
echo.
echo Próximos pasos:
echo 1. Configura Firebase: scripts\setup_firebase.bat
echo 2. Despliega infraestructura: scripts\deploy_terraform.bat
echo 3. Ejecuta el backend: scripts\run_backend.bat
echo.
pause
