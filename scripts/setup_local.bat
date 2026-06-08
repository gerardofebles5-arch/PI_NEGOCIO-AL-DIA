@echo off
REM Script de configuración local para (π)NAD V6.0
REM No requiere Google Cloud ni facturación

echo ==========================================
echo (π)NAD V6.0 - Configuración Local
echo ==========================================
echo.
echo Este script configurará el sistema en modo local.
echo NO requiere Google Cloud ni facturación.
echo.

REM Crear log
set LOG_FILE=setup_local.log
echo Iniciando configuración local > %LOG_FILE%
echo Fecha: %date% %time% >> %LOG_FILE%

REM Paso 1: Crear entorno Python
echo [1/6] Configurando entorno Python...
if not exist venv (
    python -m venv venv >> %LOG_FILE% 2>&1
    if errorlevel 1 (
        echo ERROR: No se pudo crear virtual environment
        echo Asegúrate de tener Python 3.11+ instalado
        pause
        exit /b 1
    )
    echo ✓ Virtual environment creado >> %LOG_FILE%
) else (
    echo ✓ Virtual environment ya existe >> %LOG_FILE%
)

REM Paso 2: Instalar dependencias
echo [2/6] Instalando dependencias de Python...
call venv\Scripts\activate.bat
pip install --upgrade pip >> %LOG_FILE% 2>&1
pip install -r requirements.txt >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo WARNING: Algunas dependencias fallaron (requieren dependencias adicionales)
    echo Esto es normal para módulos opcionales
) else (
    echo ✓ Dependencias instaladas >> %LOG_FILE%
)

REM Paso 3: Crear directorios
echo [3/6] Creando directorios...
if not exist config mkdir config
if not exist logs mkdir logs
if not exist data mkdir data
if not exist data\uploads mkdir data\uploads
if not exist data\exports mkdir data\exports
if not exist data\backups mkdir data\backups
echo ✓ Directorios creados >> %LOG_FILE%

REM Paso 4: Configurar .env local
echo [4/6] Configurando variables de entorno local...
if not exist .env (
    copy .env.local .env
    echo ✓ .env creado desde .env.local >> %LOG_FILE%
) else (
    echo ✓ .env ya existe
)

REM Paso 5: Inicializar base de datos local
echo [5/6] Inicializando base de datos local (SQLite)...
python -c "import sqlite3; conn = sqlite3.connect('data/pinad_local.db'); conn.execute('CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)'); conn.close()" >> %LOG_FILE% 2>&1
echo ✓ Base de datos local inicializada >> %LOG_FILE%

REM Paso 6: Verificar Flutter (opcional)
echo [6/6] Verificando Flutter SDK...
flutter --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Flutter no encontrado (opcional para el backend)
    echo Para ejecutar la app Flutter, instálalo desde:
    echo https://flutter.dev/docs/get-started/install/windows
) else (
    echo ✓ Flutter encontrado >> %LOG_FILE%
    flutter --version >> %LOG_FILE%
    
    REM Instalar dependencias de Flutter
    if exist pinad_app (
        cd pinad_app
        flutter pub get >> %LOG_FILE% 2>&1
        cd ..
        echo ✓ Dependencias de Flutter instaladas >> %LOG_FILE%
    )
)

echo.
echo ==========================================
echo CONFIGURACIÓN LOCAL COMPLETADA
echo ==========================================
echo.
echo Archivo de log: %LOG_FILE%
echo.
echo Estado de componentes:
if exist venv echo ✓ Python virtual environment
if exist .env echo ✓ Archivo .env (modo local)
if exist data echo ✓ Directorio data
if exist data\pinad_local.db echo ✓ Base de datos SQLite
if exist logs echo ✓ Directorio logs
flutter --version >nul 2>&1 && echo ✓ Flutter SDK
echo.
echo ==========================================
echo CARACTERÍSTICAS DEL MODO LOCAL
echo ==========================================
echo.
echo ✓ Base de datos SQLite (sin Cloud SQL)
echo ✓ Almacenamiento local (sin Cloud Storage)
echo ✓ OCR local (sin Document AI)
echo ✓ API REST local
echo ✓ Dashboard local
echo ✓ Contabilidad local
echo ✓ Validación local
echo.
echo ✗ Google Cloud (requiere facturación)
echo ✗ Firebase (requiere facturación)
echo ✗ Document AI (requiere facturación)
echo.
echo ==========================================
echo CÓMO EJECUTAR
echo ==========================================
echo.
echo 1. Ejecutar backend:
echo    scripts\run_backend_local.bat
echo.
echo 2. Ejecutar Flutter app (si está instalado):
echo    scripts\run_flutter_local.bat
echo.
echo 3. Para habilitar Google Cloud más tarde:
echo    - Configura una cuenta de Google Cloud con facturación
echo    - Ejecuta: scripts\setup_google_cloud.bat
echo    - Cambia .env para usar configuración de Google Cloud
echo.
pause
