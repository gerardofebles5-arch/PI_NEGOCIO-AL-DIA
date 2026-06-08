# Documentación de Despliegue Completo - (π)NAD V6.0

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración del Entorno](#configuración-del-entorno)
3. [Despliegue en Google Cloud](#despliegue-en-google-cloud)
4. [Despliegue de Flutter App](#despliegue-de-flutter-app)
5. [Configuración de CI/CD](#configuración-de-cicd)
6. [Monitoreo y Logging](#monitoreo-y-logging)
7. [Troubleshooting](#troubleshooting)
8. [Mantenimiento](#mantenimiento)

---

## Requisitos Previos

### Software Requerido

- **Google Cloud SDK** (gcloud) - versión 447.0.0 o superior
- **Terraform** - versión 1.5.0 o superior
- **Docker** - versión 24.0.0 o superior
- **Python** - versión 3.11 o superior
- **Flutter SDK** - versión 3.16.0 o superior
- **Node.js** - versión 18 LTS o superior
- **Git** - versión 2.40.0 o superior

### Cuentas y Servicios

- **Google Cloud Project** con los siguientes APIs habilitados:
  - Cloud Run
  - Cloud Functions
  - Cloud Build
  - Cloud Storage
  - Cloud SQL
  - Secret Manager
  - Cloud KMS
  - Document AI
  - Vertex AI
  - BigQuery
  - API Gateway
  - Pub/Sub

- **Firebase Project** con:
  - Authentication
  - Cloud Messaging
  - Analytics
  - Crashlytics
  - Performance Monitoring

---

## Configuración del Entorno

### 1. Configurar Google Cloud SDK

```bash
# Instalar gcloud SDK
curl https://sdk.cloud.google.com | bash

# Inicializar gcloud
gcloud init

# Configurar proyecto
gcloud config set project YOUR_PROJECT_ID
gcloud config set region us-central1

# Autenticarse
gcloud auth login
gcloud auth application-default login
```

### 2. Configurar Terraform

```bash
# Instalar Terraform
# Windows: Descargar desde https://www.terraform.io/downloads
# Linux/Mac: Usar package manager

# Verificar instalación
terraform --version

# Inicializar Terraform
cd D:\NAD\terraform
terraform init
```

### 3. Configurar Variables de Entorno

Crear archivo `terraform.tfvars`:

```hcl
project_id = "your-project-id"
region = "us-central1"
zone = "us-central1-a"

# Database
db_instance_name = "pinad-db"
db_name = "pinad"
db_user = "pinad_user"

# API Gateway
api_gateway_name = "pinad-api-gateway"

# Secrets
secrets = {
  DATABASE_URL = "postgresql://user:password@host:port/dbname"
  API_KEY = "your-api-key"
  FIREBASE_PROJECT_ID = "your-firebase-project-id"
}
```

---

## Despliegue en Google Cloud

### 1. Infraestructura con Terraform

```bash
# Planificar despliegue
cd D:\NAD\terraform
terraform plan -out=tfplan

# Aplicar cambios
terraform apply tfplan

# Verificar estado
terraform show
```

### 2. Despliegue de Cloud Functions

```bash
# Desplegar función OCR Ultra
cd D:\NAD\cloud_functions\python_functions
gcloud functions deploy ocr_ultra \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --memory=2048MB \
  --timeout=540s \
  --region=us-central1 \
  --entry-point=ocr_ultra_advanced_handler

# Desplegar función de gestión de secretos
gcloud functions deploy secret_manager \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --memory=512MB \
  --timeout=60s \
  --region=us-central1
```

### 3. Despliegue de Cloud Run

```bash
# Construir imagen Docker
cd D:\NAD
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/pinad-api:latest

# Desplegar en Cloud Run
gcloud run deploy pinad-api \
  --image gcr.io/YOUR_PROJECT_ID/pinad-api:latest \
  --platform managed \
  --region us-central1 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=10 \
  --min-instances=1 \
  --allow-unauthenticated \
  --set-env-vars=PORT=8080
```

### 4. Configurar API Gateway

```bash
# Crear API Gateway
gcloud api-gateway gateways create pinad-gateway-prod \
  --api=pinad-api-gateway \
  --api-config=pinad-api-config-prod \
  --location=us-central1
```

---

## Despliegue de Flutter App

### 1. Configurar Firebase en Flutter

```bash
# Instalar Flutter CLI
flutter pub global activate flutterfire_cli

# Configurar Firebase
cd D:\NAD\pinad_app
flutterfire configure \
  --project=your-firebase-project-id \
  --platforms=android,ios,web
```

### 2. Compilar para Android

```bash
# Configurar keystore
keytool -genkey -v -keystore pinad-release.keystore -alias pinad -keyalg RSA -keysize 2048 -validity 10000

# Compilar APK release
cd D:\NAD\pinad_app
flutter build apk --release

# Compilar App Bundle (para Play Store)
flutter build appbundle --release
```

### 3. Compilar para iOS

```bash
# Configurar firma de código
cd D:\NAD\pinad_app\ios
flutter build ios --release

# Subir a App Store Connect
xcodebuild -workspace Runner.xcworkspace -scheme Runner -archivePath Runner.xcarchive archive
xcodebuild -exportArchive -archivePath Runner.xcarchive -exportPath build
```

### 4. Compilar para Web

```bash
# Compilar para web
cd D:\NAD\pinad_app
flutter build web --release

# Desplegar en Firebase Hosting
firebase deploy --only hosting
```

---

## Configuración de CI/CD

### 1. Cloud Build para Backend

El archivo `terraform/cloudbuild.yaml` ya está configurado. Para activarlo:

```bash
# Crear trigger de Cloud Build
gcloud builds triggers create cloud-source-repositories \
  --name=pinad-backend-trigger \
  --repo=pinad-repo \
  --branch-pattern=main \
  --build-config=terraform/cloudbuild.yaml
```

### 2. Cloud Build para Terraform

```bash
# Crear trigger para Terraform
gcloud builds triggers create cloud-source-repositories \
  --name=pinad-terraform-trigger \
  --repo=pinad-repo \
  --branch-pattern=main \
  --build-config=terraform/terraform-cloudbuild.yaml
```

### 3. GitHub Actions para Flutter

Crear archivo `.github/workflows/flutter.yml`:

```yaml
name: Flutter CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
      
      - name: Install dependencies
        run: flutter pub get
      
      - name: Run tests
        run: flutter test
      
      - name: Build APK
        run: flutter build apk --release
      
      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: release-apk
          path: build/app/outputs/flutter-apk/app-release.apk
```

---

## Monitoreo y Logging

### 1. Configurar Cloud Logging

```bash
# Ver logs de Cloud Run
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=50 \
  --format="table(timestamp,severity,logName,textPayload)"

# Ver logs de Cloud Functions
gcloud logging read "resource.type=cloud_function" \
  --limit=50 \
  --format="table(timestamp,severity,logName,textPayload)"
```

### 2. Configurar Cloud Monitoring

```bash
# Crear dashboard
gcloud monitoring dashboards create pinad-dashboard \
  --config-from-file=monitoring/dashboard.json

# Crear alertas
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring/alert-policy.json
```

### 3. Configurar Firebase Crashlytics

```bash
# Subir símbolos de Android
flutter build apk --release
firebase crashlytics:symbols:upload --app=your-firebase-project-id
```

---

## Troubleshooting

### Problemas Comunes

#### 1. Error de autenticación de Google Cloud

```bash
# Re-autenticarse
gcloud auth login
gcloud auth application-default login
```

#### 2. Error de conexión a base de datos

```bash
# Verificar conexión SQL
gcloud sql connect pinad-db --user=pinad_user

# Verificar IP autorizada
gcloud sql instances describe pinad-db --format="value(ipAddresses)"
```

#### 3. Error de compilación de Flutter

```bash
# Limpiar caché de Flutter
flutter clean
flutter pub get
```

#### 4. Error de despliegue de Cloud Functions

```bash
# Verificar logs de despliegue
gcloud functions logs read ocr_ultra --limit=50

# Reintentar despliegue
gcloud functions deploy ocr_ultra --force
```

---

## Mantenimiento

### 1. Actualizaciones de Seguridad

```bash
# Actualizar dependencias de Python
pip install --upgrade -r requirements.txt

# Actualizar dependencias de Flutter
flutter pub upgrade
```

### 2. Backups de Base de Datos

```bash
# Crear backup
gcloud sql backups create pinad-db-backup \
  --instance=pinad-db \
  --description="Backup manual"

# Listar backups
gcloud sql backups list --instance=pinad-db
```

### 3. Rotación de Secrets

```bash
# Actualizar secret en Secret Manager
echo "new-secret-value" | gcloud secrets versions add DATABASE_SECRET --data-file=-

# Verificar versión
gcloud secrets versions list DATABASE_SECRET
```

### 4. Escalado Automático

```bash
# Configurar escalado de Cloud Run
gcloud run services update pinad-api \
  --max-instances=20 \
  --min-instances=2 \
  --cpu-threshold=60
```

---

## Referencias

- [Documentación de Google Cloud Run](https://cloud.google.com/run/docs)
- [Documentación de Cloud Functions](https://cloud.google.com/functions/docs)
- [Documentación de Terraform](https://www.terraform.io/docs)
- [Documentación de Flutter](https://flutter.dev/docs)
- [Documentación de Firebase](https://firebase.google.com/docs)

---

## Soporte

Para soporte técnico, contactar a:
- Email: support@piadmin.com
- Documentación: docs.pinad.com
- Issues: github.com/pinad/nad/issues
