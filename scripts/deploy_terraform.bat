@echo off
REM Script de despliegue automático con Terraform para Windows

echo ==========================================
echo Despliegue Automático con Terraform
echo ==========================================
echo.

REM Verificar si terraform está instalado
terraform --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Terraform no está instalado
    echo Por favor instálalo desde:
    echo https://learn.hashicorp.com/tutorials/terraform/install-cli
    pause
    exit /b 1
)

echo ✓ Terraform encontrado
echo.

REM Verificar si existe directorio terraform
if not exist terraform (
    echo ERROR: Directorio terraform no encontrado
    echo Crea el directorio terraform con tus archivos de configuración
    pause
    exit /b 1
)

cd terraform

REM Inicializar Terraform
echo [1/4] Inicializando Terraform...
terraform init
if errorlevel 1 (
    echo ERROR: No se pudo inicializar Terraform
    pause
    exit /b 1
)
echo ✓ Terraform inicializado
echo.

REM Validar configuración
echo [2/4] Validando configuración...
terraform validate
if errorlevel 1 (
    echo ERROR: Configuración de Terraform inválida
    pause
    exit /b 1
)
echo ✓ Configuración válida
echo.

REM Planificar despliegue
echo [3/4] Planificando despliegue...
terraform plan -out=tfplan
if errorlevel 1 (
    echo ERROR: No se pudo crear el plan de despliegue
    pause
    exit /b 1
)
echo ✓ Plan creado
echo.

REM Aplicar despliegue
echo [4/4] Aplicando despliegue...
echo Esto puede tomar varios minutos...
terraform apply tfplan
if errorlevel 1 (
    echo ERROR: No se pudo aplicar el despliegue
    pause
    exit /b 1
)
echo ✓ Infraestructura desplegada
echo.

REM Mostrar outputs
echo Mostrando outputs...
terraform output
echo.

cd ..

echo ==========================================
echo Despliegue completado
echo ==========================================
echo.
echo Próximos pasos:
echo 1. Ejecuta el backend: scripts\run_backend.bat
echo 2. Ejecuta la app Flutter: scripts\run_flutter.bat
echo.
pause
