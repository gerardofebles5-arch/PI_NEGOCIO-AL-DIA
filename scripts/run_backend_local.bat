@echo off
REM Script para ejecutar el backend en modo local (sin Google Cloud)

echo ==========================================
echo (π)NAD V6.0 - Backend (Modo Local)
echo ==========================================
echo.

REM Activar virtual environment
call venv\Scripts\activate.bat

REM Verificar si .env existe
if not exist .env (
    echo ERROR: Archivo .env no encontrado
    echo Ejecuta: scripts\setup_local.bat
    pause
    exit /b 1
)

REM Verificar si existe base de datos local
if not exist data\pinad_local.db (
    echo Inicializando base de datos local...
    python -c "import sqlite3; conn = sqlite3.connect('data/pinad_local.db'); conn.execute('CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)'); conn.close()"
)

REM Establecer modo local
set USE_LOCAL_DB=true
set GOOGLE_CLOUD_ENABLED=false
set FIREBASE_ENABLED=false

REM Ejecutar backend
echo.
echo Iniciando backend en modo local...
echo (Sin Google Cloud - sin facturación)
echo.
python main.py

pause
