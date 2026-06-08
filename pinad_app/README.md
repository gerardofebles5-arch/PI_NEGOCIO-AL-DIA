# (π)NAD - Contabilidad Automatizada

Aplicación Flutter multiplataforma para contabilidad automatizada con Google Cloud Native Architecture.

## Características

- **Multiplataforma**: iOS, Android, Web, Desktop (Windows, macOS, Linux)
- **Autenticación**: Firebase Authentication con OAuth2 y Google Sign-In
- **State Management**: BLoC/Cubit pattern con flutter_bloc
- **Material Design 3**: UI moderna con soporte para dark mode
- **Internacionalización**: Español e inglés
- **Métricas en tiempo real**: Dashboard con datos de BigQuery
- **Offline-first**: Soporte para modo offline con sincronización
- **Notificaciones**: Firebase Cloud Messaging

## Arquitectura

El proyecto sigue el patrón de Clean Architecture:

```
lib/
├── core/
│   ├── constants/       # Constantes de la aplicación
│   ├── theme/          # Temas y estilos
│   ├── utils/          # Utilidades y helpers
│   └── errors/         # Manejo de errores
├── data/
│   ├── models/         # Modelos de datos
│   ├── repositories/   # Implementación de repositorios
│   └── datasources/    # Fuentes de datos (API, Firebase)
├── domain/
│   ├── entities/       # Entidades del dominio
│   ├── usecases/       # Casos de uso
│   └── repositories/   # Interfaces de repositorios
└── presentation/
    ├── pages/          # Pantallas
    ├── widgets/        # Widgets reutilizables
    ├── cubit/          # State management (BLoC/Cubit)
    └── routes/         # Rutas de navegación
```

## Tecnologías

### Frontend
- **Flutter 3.24+**: Framework multiplataforma
- **flutter_bloc**: State management
- **Material Design 3**: Sistema de diseño
- **easy_localization**: Internacionalización

### Backend (Google Cloud)
- **Firebase Authentication**: Autenticación
- **Cloud Functions**: Backend serverless
- **BigQuery**: Data warehouse
- **Cloud Storage**: Almacenamiento de archivos
- **Cloud Messaging**: Notificaciones push
- **Crashlytics**: Crash reporting
- **Performance Monitoring**: Monitoreo de performance

## Instalación

### Prerrequisitos
- Flutter SDK 3.24 o superior
- Dart 3.0 o superior
- Android Studio / VS Code
- Firebase project configurado

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/pinad/pinad_app.git
cd pinad_app
```

2. **Instalar dependencias**
```bash
flutter pub get
```

3. **Configurar Firebase**
```bash
flutterfire configure
```

4. **Ejecutar la aplicación**
```bash
# Debug mode
flutter run

# Release mode
flutter run --release
```

## Configuración de Firebase

1. Crear un proyecto en [Firebase Console](https://console.firebase.google.com/)
2. Agregar apps de iOS, Android y Web
3. Habilitar Authentication (Email/Password, Google Sign-In)
4. Habilitar Cloud Functions
5. Habilitar BigQuery
6. Habilitar Cloud Messaging
7. Descargar `google-services.json` para Android
8. Descargar `GoogleService-Info.plist` para iOS

## Scripts útiles

### Build para producción
```bash
# Android APK
flutter build apk --release

# Android App Bundle
flutter build appbundle --release

# iOS
flutter build ios --release

# Web
flutter build web --release

# Windows
flutter build windows --release

# macOS
flutter build macos --release

# Linux
flutter build linux --release
```

### Testing
```bash
# Unit tests
flutter test

# Integration tests
flutter test integration_test/

# Coverage
flutter test --coverage
```

### Linting
```bash
flutter analyze
```

## CI/CD

El proyecto usa GitHub Actions para CI/CD:

- **Build automático** en cada push
- **Tests automáticos** en cada PR
- **Despliegue automático** a Firebase Hosting en main branch

## Estructura de pantallas

- **Splash**: Pantalla de carga
- **Login**: Inicio de sesión
- **Register**: Registro de usuarios
- **Forgot Password**: Recuperación de contraseña
- **Dashboard**: Dashboard principal con métricas
- **Documents**: Gestión de documentos
- **Accounting**: Contabilidad
- **Reports**: Reportes
- **Settings**: Configuración

## State Management

El proyecto usa el patrón BLoC/Cubit:

- **AuthCubit**: Gestión de autenticación
- **DashboardCubit**: Gestión de métricas del dashboard
- **DocumentCubit**: Gestión de documentos
- **AccountingCubit**: Gestión de contabilidad

## Internacionalización

La aplicación soporta:
- Español (es)
- Inglés (en)

Los archivos de traducción están en `assets/translations/`.

## Temas

La aplicación soporta:
- Light mode
- Dark mode
- System mode (sigue la configuración del sistema)

## Seguridad

- OAuth2 con Firebase Authentication
- JWT tokens para sesiones
- Refresh tokens para renovación automática
- Cifrado de datos sensibles con flutter_secure_storage
- Certificate pinning para APIs críticas

## Performance

- Lazy loading de componentes
- Caching de imágenes con cached_network_image
- Optimización de builds con tree-shaking
- Code splitting para web

## Testing

- **Unit tests**: Lógica de negocio pura
- **Widget tests**: UI components
- **Integration tests**: Flujos completos
- **Golden tests**: Visual regression testing

## Monitoreo

- **Firebase Crashlytics**: Crash reporting
- **Firebase Performance Monitoring**: Performance tracking
- **Firebase Analytics**: User analytics
- **Cloud Logging**: Logging centralizado

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.

## Contacto

- **Email**: contact@pinad.com
- **Website**: https://pinad.com
- **Documentación**: https://docs.pinad.com

## Roadmap

- [x] Fase 1: Cimiento Operativo
- [x] Fase 2: Cerebro Automatizado
- [ ] Fase 3: Interfaces Nativas (En progreso)
- [ ] Fase 4: Implementación Final

## Acknowledgments

- Google Cloud Platform
- Firebase
- Flutter Team
- Material Design Team
