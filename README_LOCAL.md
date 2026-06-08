# (π)NAD V6.0 - Modo Local

## Descripción
Esta versión de (π)NAD V6.0 funciona completamente en modo local sin requerir Google Cloud ni facturación.

## Características del Modo Local
- ✅ Base de datos SQLite local
- ✅ Almacenamiento local de archivos
- ✅ API REST local
- ✅ Contabilidad completa
- ✅ OCR local
- ✅ Validación de documentos
- ✅ Dashboard local
- ✅ Cálculo de impuestos
- ✅ Generación de reportes

## Lo que NO requiere
- ❌ Google Cloud (sin facturación)
- ❌ Firebase (sin facturación)
- ❌ Document AI (sin facturación)
- ❌ Cloud SQL (sin facturación)
- ❌ Cloud Storage (sin facturación)

## Instalación

### Backend (Python)
```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar backend
python main.py
```

### App Flutter
```bash
# 1. Instalar Flutter SDK (si no está instalado)
# Descargar desde: https://flutter.dev/docs/get-started/install/windows

# 2. Ir al directorio de la app
cd pinad_app

# 3. Instalar dependencias
flutter pub get

# 4. Ejecutar app
flutter run
```

## Scripts Automatizados

### Setup Local Completo
```bash
scripts\setup_local.bat
```

### Ejecutar Backend Local
```bash
scripts\run_backend_local.bat
```

### Ejecutar Flutter Local
```bash
scripts\run_flutter_local.bat
```

## Configuración

El archivo `.env` contiene la configuración local:
- `USE_LOCAL_DB=true` - Usa base de datos SQLite
- `GOOGLE_CLOUD_ENABLED=false` - Desactiva Google Cloud
- `FIREBASE_ENABLED=false` - Desactiva Firebase

## Estructura de Directorios

```
D:\NAD\
├── data/
│   ├── pinad_local.db          # Base de datos SQLite
│   ├── uploads/                # Archivos subidos
│   ├── exports/                # Archivos exportados
│   └── backups/                # Backups
├── config/
│   ├── config.py               # Configuración estándar
│   └── config_local.py         # Configuración local
├── logs/                       # Logs del sistema
├── src/                        # Código fuente del backend
├── pinad_app/                  # App Flutter
│   └── lib/
│       └── config/
│           └── local_config.dart # Configuración local Flutter
└── scripts/                    # Scripts automatizados
    ├── setup_local.bat
    ├── run_backend_local.bat
    └── run_flutter_local.bat
```

## API Endpoints

El backend expone los siguientes endpoints en `http://localhost:5000`:

### Health Check
- `GET /health` - Verifica estado del sistema

### Documentos
- `POST /api/documents` - Subir documento
- `GET /api/documents` - Listar documentos
- `GET /api/documents/{id}` - Obtener documento
- `DELETE /api/documents/{id}` - Eliminar documento

### OCR
- `POST /api/ocr/process` - Procesar documento con OCR

### Contabilidad
- `GET /api/accounting/statements` - Estados financieros
- `GET /api/accounting/ledger` - Libro mayor
- `POST /api/accounting/transactions` - Crear transacción

### Impuestos
- `POST /api/tax/calculate` - Calcular impuestos
- `GET /api/tax/declarations` - Listar declaraciones

## Soporte

Para problemas o preguntas:
1. Revisa el archivo de logs en `logs/pinad_local.log`
2. Verifica que el backend esté ejecutándose
3. Verifica que la base de datos `data/pinad_local.db` exista
4. Verifica que los directorios de datos existan

## Actualización a Google Cloud

Si en el futuro deseas usar Google Cloud:
1. Configura una cuenta de Google Cloud con facturación
2. Ejecuta `scripts\setup_google_cloud.bat`
3. Cambia `.env` para usar configuración de Google Cloud
4. Despliega la infraestructura con Terraform
