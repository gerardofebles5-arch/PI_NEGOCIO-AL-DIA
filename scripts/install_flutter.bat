@echo off
REM Script de instalación automática de Flutter SDK para Windows

echo ==========================================
echo Instalación Automática de Flutter SDK
echo ==========================================
echo.

REM Variables
set FLUTTER_VERSION=3.16.0
set FLUTTER_DIR=C:\flutter
set FLUTTER_ZIP=flutter_windows_%FLUTTER_VERSION%.zip
set FLUTTER_URL=https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/%FLUTTER_ZIP%
set TEMP_DIR=%TEMP%\flutter_install

echo Versión de Flutter: %FLUTTER_VERSION%
echo Directorio de instalación: %FLUTTER_DIR%
echo.

REM Verificar si Flutter ya está instalado
if exist "%FLUTTER_DIR%\bin\flutter.bat" (
    echo Flutter ya está instalado en %FLUTTER_DIR%
    flutter --version
    echo.
    echo ¿Deseas reinstalar? (S/N)
    choice /C SN /N
    if errorlevel 2 (
        echo Manteniendo instalación existente
        exit /b 0
    )
)

REM Verificar si hay conexión a internet
echo Verificando conexión a internet...
ping -n 1 google.com >nul 2>&1
if errorlevel 1 (
    echo ERROR: No hay conexión a internet
    echo No se puede descargar Flutter automáticamente
    echo Por favor descárgalo manualmente desde:
    echo https://flutter.dev/docs/get-started/install/windows
    pause
    exit /b 1
)

echo ✓ Conexión a internet disponible
echo.

REM Crear directorio temporal
echo Creando directorio temporal...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

REM Descargar Flutter
echo Descargando Flutter SDK (%FLUTTER_VERSION%)...
echo Esto puede tomar varios minutos...
curl -L -o "%TEMP_DIR%\%FLUTTER_ZIP%" %FLUTTER_URL%
if errorlevel 1 (
    echo ERROR: No se pudo descargar Flutter
    echo Por favor descárgalo manualmente desde:
    echo https://flutter.dev/docs/get-started/install/windows
    pause
    exit /b 1
)

echo ✓ Flutter descargado
echo.

REM Extraer Flutter
echo Extrayendo Flutter SDK...
tar -xf "%TEMP_DIR%\%FLUTTER_ZIP%" -C "%TEMP_DIR%"
if errorlevel 1 (
    echo ERROR: No se pudo extraer Flutter
    pause
    exit /b 1
)

echo ✓ Flutter extraído
echo.

REM Mover al directorio final
echo Instalando Flutter en %FLUTTER_DIR%...
if exist "%FLUTTER_DIR%" rmdir /s /q "%FLUTTER_DIR%"
move "%TEMP_DIR%\flutter" "%FLUTTER_DIR%"
if errorlevel 1 (
    echo ERROR: No se pudo mover Flutter al directorio final
    echo Intenta ejecutar como administrador
    pause
    exit /b 1
)

echo ✓ Flutter instalado
echo.

REM Limpiar directorio temporal
echo Limpiando archivos temporales...
rmdir /s /q "%TEMP_DIR%"

REM Agregar Flutter al PATH
echo Agregando Flutter al PATH del sistema...
setx PATH "%PATH%;%FLUTTER_DIR%\bin" /M >nul 2>&1
if errorlevel 1 (
    echo WARNING: No se pudo agregar Flutter al PATH del sistema
    echo Se requieren permisos de administrador
    echo Agrega manualmente %FLUTTER_DIR%\bin a tu PATH
    echo.
    echo O ejecuta este script como administrador
) else (
    echo ✓ Flutter agregado al PATH del sistema
)

REM Actualizar PATH actual
set PATH=%PATH%;%FLUTTER_DIR%\bin

REM Ejecutar flutter doctor
echo.
echo Ejecutando flutter doctor...
flutter doctor
echo.

REM Ejecutar flutter precache
echo Ejecutando flutter precache...
flutter precache
echo.

echo ==========================================
echo Instalación de Flutter completada
echo ==========================================
echo.
echo Directorio de instalación: %FLUTTER_DIR%
echo.
echo IMPORTANTE:
echo 1. Cierra y vuelve a abrir esta terminal para que el PATH se actualice
echo 2. O ejecuta: set PATH=%PATH%;%FLUTTER_DIR%\bin
echo.
echo Verifica la instalación ejecutando:
echo   flutter --version
echo.
pause
