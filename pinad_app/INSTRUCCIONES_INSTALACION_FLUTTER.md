# Instrucciones para Instalar Flutter SDK en Windows

## Fecha
Junio 8, 2026

## Paso 1: Descargar Flutter SDK

1. Ve a la página oficial de Flutter: https://flutter.dev/docs/get-started/install/windows
2. Descarga la última versión estable de Flutter SDK para Windows
3. Descomprime el archivo ZIP en una carpeta, por ejemplo: `C:\flutter`

## Paso 2: Configurar Variables de Entorno

### Agregar Flutter al PATH

1. Presiona la tecla `Windows` y busca "Variables de entorno"
2. Selecciona "Editar las variables de entorno del sistema"
3. En "Variables del sistema", busca la variable `Path` y selecciona "Editar"
4. Agrega la ruta completa al directorio `bin` de Flutter:
   - `C:\flutter\bin`
5. Acepta todos los cambios

### Verificar instalación

Abre una nueva terminal de PowerShell y ejecuta:

```powershell
flutter --version
```

Deberías ver la versión de Flutter instalada.

## Paso 3: Instalar Dependencias Adicionales

### Visual Studio Build Tools

1. Descarga Visual Studio Build Tools desde: https://visualstudio.microsoft.com/downloads/
2. Instala "Desktop development with C++"
3. Asegúrate de incluir "Windows 10 SDK" o "Windows 11 SDK"

### Git

1. Descarga Git desde: https://git-scm.com/download/win
2. Instala Git con las opciones por defecto

### Android Studio (opcional, para desarrollo móvil)

1. Descarga Android Studio desde: https://developer.android.com/studio
2. Instala Android Studio
3. Configura Android SDK en Android Studio
4. Acepta las licencias de Android:
   ```powershell
   flutter doctor --android-licenses
   ```

## Paso 4: Verificar Instalación

Ejecuta el comando de diagnóstico de Flutter:

```powershell
flutter doctor
```

Este comando verificará todas las dependencias necesarias. Deberías ver algo como:

```
[✓] Flutter (Channel stable, 3.x.x, on Microsoft Windows [Version x.x.x])
[✓] Android toolchain - develop for Android devices
[✓] Chrome - develop for the web
[✓] Visual Studio - develop for Windows apps
[✓] VS Code (version x.x.x)
[✓] Connected device (available)
```

## Paso 5: Configurar Flutter Web

Para el desarrollo web, asegúrate de que Chrome esté instalado y configurado:

```powershell
flutter config --enable-web
```

## Paso 6: Actualizar Dependencias del Proyecto

Una vez que Flutter esté instalado, navega al directorio del proyecto y ejecuta:

```powershell
cd D:\NAD\pinad_app
flutter pub get
```

## Paso 7: Build de Flutter Web

Para construir la aplicación web:

```powershell
flutter build web
```

El build se generará en: `D:\NAD\pinad_app\build\web`

## Paso 8: Desplegar en Firebase Hosting

Una vez que el build esté completo, despliega en Firebase Hosting:

```powershell
firebase deploy
```

## Solución de Problemas Comunes

### Error: "flutter no se reconoce como un comando interno o externo"

- Cierra todas las terminales abiertas
- Abre una nueva terminal
- Verifica que Flutter esté en el PATH
- Reinicia el equipo si es necesario

### Error: "No se encontró Visual Studio"

- Instala Visual Studio Build Tools
- Asegúrate de incluir "Desktop development with C++"
- Reinicia la terminal

### Error: "No se encontró Android SDK"

- Instala Android Studio
- Configura Android SDK en Android Studio
- Acepta las licencias de Android con `flutter doctor --android-licenses`

## Próximos Pasos

Una vez que Flutter esté instalado y configurado:

1. Ejecutar `flutter pub get` para actualizar dependencias
2. Ejecutar `flutter build web` para construir la aplicación
3. Ejecutar `firebase deploy` para desplegar en Firebase Hosting
4. Probar la aplicación en producción en: https://pinad-scanning-system-cbde8.web.app
