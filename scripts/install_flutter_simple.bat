@echo off
REM Script simple de instalación de Flutter

echo Instalando Flutter SDK...
echo.

REM Descargar Flutter
echo Descargando Flutter 3.16.0...
powershell -Command "Invoke-WebRequest -Uri 'https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.16.0-stable.zip' -OutFile 'flutter.zip'"

if errorlevel 1 (
    echo ERROR: No se pudo descargar Flutter
    echo Por favor descárgalo manualmente desde:
    echo https://flutter.dev/docs/get-started/install/windows
    pause
    exit /b 1
)

echo Flutter descargado
echo.

REM Extraer Flutter
echo Extrayendo Flutter...
powershell -Command "Expand-Archive -Path 'flutter.zip' -DestinationPath 'C:\' -Force"

if errorlevel 1 (
    echo ERROR: No se pudo extraer Flutter
    pause
    exit /b 1
)

echo Flutter extraído a C:\flutter
echo.

REM Limpiar
del flutter.zip

REM Agregar al PATH
echo Agregando Flutter al PATH...
setx PATH "%PATH%;C:\flutter\bin" /M

echo.
echo ==========================================
echo Instalación de Flutter completada
echo ==========================================
echo.
echo IMPORTANTE: Cierra y vuelve a abrir esta terminal
echo para que el PATH se actualice.
echo.
echo Luego verifica con: flutter --version
echo.
pause
