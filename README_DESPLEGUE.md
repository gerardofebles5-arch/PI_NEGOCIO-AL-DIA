# (π)NAD V6.0 - Guía de Despliegue Rápido

## Despliegue Rápido en Google Cloud

### 1. Configurar Proyecto

```bash
# Clonar repositorio
git clone https://github.com/pinad/nad.git
cd nad

# Configurar gcloud
gcloud config set project YOUR_PROJECT_ID
gcloud config set region us-central1
```

### 2. Desplegar Infraestructura

```bash
cd terraform
terraform init
terraform apply
```

### 3. Desplegar Backend

```bash
# Cloud Functions
gcloud functions deploy ocr_ultra --runtime python311 --trigger-http

# Cloud Run
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/pinad-api
gcloud run deploy pinad-api --image gcr.io/YOUR_PROJECT_ID/pinad-api
```

### 4. Desplegar Flutter App

```bash
cd pinad_app
flutter build apk --release
flutter build appbundle --release
```

### 5. Verificar Despliegue

```bash
# Verificar Cloud Run
gcloud run services describe pinad-api

# Verificar Cloud Functions
gcloud functions describe ocr_ultra

# Ver logs
gcloud logging read "resource.type=cloud_run_revision"
```

## URLs de Despliegue

- **API REST**: `https://pinad-api-<hash>.a.run.app`
- **API Gateway**: `https://pinad-gateway-<hash>.gateway.cloud.goog`
- **Flutter Web**: `https://pinad.web.app`

## Soporte

Para ayuda adicional, ver `docs/DESPLEGUE_COMPLETO.md`
