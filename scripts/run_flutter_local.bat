@echo off
REM Script para ejecutar la app Flutter en modo local (sin Google Cloud)

echo ==========================================
echo (π)NAD V6.0 - Flutter App (Modo Local)
echo ==========================================
echo.

cd pinad_app

REM Verificar si .env existe en el directorio raíz
if not exist ..\.env (
    echo ERROR: Archivo .env no encontrado en directorio raíz
    echo Ejecuta: scripts\setup_local.bat
    pause
    exit /b 1
)

REM Verificar si Flutter está instalado
flutter --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Flutter no está instalado
    echo Instálalo desde: https://flutter.dev/docs/get-started/install/windows
    pause
    exit /b 1
)

REM Instalar dependencias
echo.
echo Instalando dependencias de Flutter...
flutter pub get

REM Ejecutar app
echo.
echo Iniciando Flutter app en modo local...
echo (Sin Google Cloud - sin facturación)
echo.
flutter run

pause
