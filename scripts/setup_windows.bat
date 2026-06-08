@echo off
REM Script para configurar (π)NAD V6.0 en Windows

echo ==========================================
echo (π)NAD V6.0 - Windows Setup
echo ==========================================

REM 1. Crear virtual environment
echo.
echo 1. Creando virtual environment de Python...
python -m venv venv
call venv\Scripts\activate.bat

echo ✓ Virtual environment creado

REM 2. Instalar dependencias de Python
echo.
echo 2. Instalando dependencias de Python...
pip install --upgrade pip
pip install -r requirements.txt

echo ✓ Dependencias instaladas

REM 3. Crear directorios necesarios
echo.
echo 3. Creando directorios necesarios...
if not exist config mkdir config
if not exist logs mkdir logs
if not exist data mkdir data
if not exist data\uploads mkdir data\uploads
if not exist data\exports mkdir data\exports
if not exist data\backups mkdir data\backups

echo ✓ Directorios creados

REM 4. Copiar archivo .env.example
echo.
echo 4. Configurando variables de entorno...
if not exist .env (
    copy .env.example .env
    echo ✓ Archivo .env creado desde .env.example
    echo   ¡IMPORTANTE! Edita .env con tus credenciales reales
) else (
    echo ✓ Archivo .env ya existe
)

REM 5. Verificar instalación de Flutter
echo.
echo 5. Verificando instalación de Flutter...
flutter --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Flutter no encontrado. Por favor instala Flutter SDK desde:
    echo   https://flutter.dev/docs/get-started/install/windows
) else (
    echo ✓ Flutter encontrado
)

REM 6. Instalar dependencias de Flutter
echo.
echo 6. Instalando dependencias de Flutter...
cd pinad_app
flutter pub get
cd ..

echo ✓ Dependencias de Flutter instaladas

REM 7. Verificar instalación de Google Cloud SDK
echo.
echo 7. Verificando instalación de Google Cloud SDK...
gcloud --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Google Cloud SDK no encontrado. Por favor instala desde:
    echo   https://cloud.google.com/sdk/docs/install
) else (
    echo ✓ Google Cloud SDK encontrado
)

REM 8. Verificar instalación de Terraform
echo.
echo 8. Verificando instalación de Terraform...
terraform --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Terraform no encontrado. Por favor instala desde:
    echo   https://learn.hashicorp.com/tutorials/terraform/install-cli
) else (
    echo ✓ Terraform encontrado
)

echo.
echo ==========================================
echo Setup completado
echo ==========================================
echo.
echo Próximos pasos:
echo 1. Edita .env con tus credenciales reales
echo 2. Configura Google Cloud: gcloud auth login
echo 3. Configura Firebase: firebase login
echo 4. Ejecuta: python main.py
echo 5. Ejecuta Flutter: cd pinad_app && flutter run
echo.
pause
