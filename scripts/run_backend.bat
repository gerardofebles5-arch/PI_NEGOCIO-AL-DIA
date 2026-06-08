@echo off
REM Script para ejecutar el backend de (π)NAD V6.0

echo ==========================================
echo (π)NAD V6.0 - Backend
echo ==========================================

REM Activar virtual environment
call venv\Scripts\activate.bat

REM Verificar si .env existe
if not exist .env (
    echo ERROR: Archivo .env no encontrado
    echo Por favor copia .env.example a .env y configuralo
    pause
    exit /b 1
)

REM Ejecutar backend
echo.
echo Iniciando backend...
python main.py

pause
