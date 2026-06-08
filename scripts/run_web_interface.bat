@echo off
REM Script para ejecutar la interfaz web de (π)NAD

echo ==========================================
echo (π)NAD - Interfaz Web
echo ==========================================
echo.

REM Verificar si el backend está ejecutándose
echo Verificando si el backend está ejecutándose...
curl -s http://localhost:5000/api/health >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ El backend no está ejecutándose
    echo.
    echo Para iniciar el backend:
    echo   cd D:\NAD
    echo   venv\Scripts\python.exe main.py
    echo.
    pause
    exit /b 1
)

echo ✅ Backend detectado en http://localhost:5000
echo.

REM Abrir la interfaz web
echo Abriendo interfaz web...
start "" "D:\NAD\web_interface\index.html"

echo.
echo ✅ Interfaz web abierta en el navegador
echo.
echo La interfaz web se conectará automáticamente al backend
echo Backend: http://localhost:5000
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
