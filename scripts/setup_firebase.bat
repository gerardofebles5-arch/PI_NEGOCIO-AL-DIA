@echo off
REM Script de configuración automática de Firebase para Windows

echo ==========================================
echo Configuración Automática de Firebase
echo ==========================================
echo.

REM Verificar si firebase-tools está instalado
firebase --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Firebase CLI no está instalado
    echo Instalando Firebase CLI...
    npm install -g firebase-tools
    if errorlevel 1 (
        echo ERROR: No se pudo instalar Firebase CLI
        echo Asegúrate de tener Node.js y npm instalados
        pause
        exit /b 1
    )
)

echo ✓ Firebase CLI encontrado
echo.

REM Login en Firebase
echo [1/6] Autenticando con Firebase...
firebase login
if errorlevel 1 (
    echo ERROR: No se pudo autenticar con Firebase
    pause
    exit /b 1
)
echo ✓ Autenticación completada
echo.

REM Crear proyecto Firebase
echo [2/6] Creando proyecto Firebase...
set /p PROJECT_ID="Ingresa tu Firebase Project ID (o presiona Enter para usar 'pinad-production'): "
if "%PROJECT_ID%"=="" set PROJECT_ID=pinad-production

firebase projects:create %PROJECT_ID%
if errorlevel 1 (
    echo WARNING: El proyecto podría ya existir
    echo Continuando con el proyecto existente...
)
echo ✓ Proyecto Firebase: %PROJECT_ID%
echo.

REM Habilitar Authentication
echo [3/6] Habilitando Authentication...
firebase auth:enable
if errorlevel 1 (
    echo WARNING: No se pudo habilitar Authentication
) else (
    echo ✓ Authentication habilitado
)
echo.

REM Habilitar Email/Password
echo Habilitando Email/Password authentication...
firebase auth:provider create email
echo.

REM Habilitar Google Sign-In
echo Habilitando Google Sign-In...
firebase auth:provider create google
echo.

REM Habilitar Cloud Messaging
echo [4/6] Habilitando Cloud Messaging...
firebase messaging:enable
if errorlevel 1 (
    echo WARNING: No se pudo habilitar Cloud Messaging
) else (
    echo ✓ Cloud Messaging habilitado
)
echo.

REM Habilitar Analytics
echo [5/6] Habilitando Analytics...
firebase analytics:enable
if errorlevel 1 (
    echo WARNING: No se pudo habilitar Analytics
) else (
    echo ✓ Analytics habilitado
)
echo.

REM Habilitar Crashlytics
echo Habilitando Crashlytics...
firebase crashlytics:enable
if errorlevel 1 (
    echo WARNING: No se pudo habilitar Crashlytics
) else (
    echo ✓ Crashlytics habilitado
)
echo.

REM Habilitar Performance Monitoring
echo Habilitando Performance Monitoring...
firebase performance:enable
if errorlevel 1 (
    echo WARNING: No se pudo habilitar Performance Monitoring
) else (
    echo ✓ Performance Monitoring habilitado
)
echo.

REM Configurar Flutter
echo [6/6] Configurando Flutter con Firebase...
if exist pinad_app (
    cd pinad_app
    flutterfire configure --project=%PROJECT_ID% --platforms=android,ios,web
    cd ..
    if errorlevel 1 (
        echo WARNING: No se pudo configurar Flutter con Firebase
        echo Ejecuta manualmente: cd pinad_app && flutterfire configure --project=%PROJECT_ID%
    ) else (
        echo ✓ Flutter configurado con Firebase
    )
) else (
    echo WARNING: Directorio pinad_app no encontrado
)
echo.

REM Obtener configuración de Firebase
echo Obteniendo configuración de Firebase...
firebase projects:list
echo.

REM Actualizar .env
echo Actualizando archivo .env...
if exist .env (
    echo FIREBASE_PROJECT_ID=%PROJECT_ID% >> .env
    echo ✓ .env actualizado
) else (
    echo WARNING: .env no encontrado
    echo Crea .env desde .env.example primero
)
echo.

echo ==========================================
echo Configuración de Firebase completada
echo ==========================================
echo.
echo Proyecto: %PROJECT_ID%
echo.
echo Próximos pasos:
echo 1. Copia google-services.json a pinad_app/android/app/
echo 2. Copia GoogleService-Info.plist a pinad_app/ios/Runner/
echo 3. Ejecuta: cd pinad_app && flutter pub get
echo 4. Ejecuta: cd pinad_app && flutter run
echo.
pause
