@echo off
REM Script para ejecutar la app Flutter de (π)NAD V6.0

echo ==========================================
echo (π)NAD V6.0 - Flutter App
echo ==========================================

cd pinad_app

REM Verificar si .env existe en el directorio raíz
if not exist ..\.env (
    echo ERROR: Archivo .env no encontrado en directorio raíz
    echo Por favor copia .env.example a .env y configuralo
    pause
    exit /b 1
)

REM Verificar si Flutter está instalado
flutter --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Flutter no está instalado
    echo Ejecuta: scripts\install_flutter.bat
    pause
    exit /b 1
)

REM Instalar dependencias
echo.
echo Instalando dependencias de Flutter...
flutter pub get

REM Ejecutar app
echo.
echo Iniciando Flutter app...
flutter run

pause
