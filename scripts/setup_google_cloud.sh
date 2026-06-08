#!/bin/bash
# Script para configurar Google Cloud Project para (π)NAD V6.0

set -e

echo "=========================================="
echo "(π)NAD V6.0 - Google Cloud Setup"
echo "=========================================="

# Variables
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"pinad-production"}
REGION=${GOOGLE_CLOUD_REGION:-"us-central1"}
ZONE="${REGION}-a"

echo "Configurando proyecto: $PROJECT_ID"
echo "Región: $REGION"

# 1. Configurar proyecto
echo ""
echo "1. Configurando proyecto de Google Cloud..."
gcloud config set project $PROJECT_ID
gcloud config set region $REGION
gcloud config set compute/zone $ZONE

# 2. Habilitar APIs requeridas
echo ""
echo "2. Habilitando APIs de Google Cloud..."
gcloud services enable \
    cloudresourcemanager.googleapis.com \
    compute.googleapis.com \
    storage.googleapis.com \
    sqladmin.googleapis.com \
    bigquery.googleapis.com \
    documentai.googleapis.com \
    aiplatform.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    apigateway.googleapis.com \
    secretmanager.googleapis.com \
    cloudkms.googleapis.com \
    pubsub.googleapis.com \
    scheduler.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    cloudaudit.googleapis.com \
    appengine.googleapis.com

echo "✓ APIs habilitadas"

# 3. Crear Service Account
echo ""
echo "3. Creando Service Account..."
SA_NAME="pinad-service-account"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create $SA_NAME \
    --display-name="PINAD Service Account" \
    --description="Service account for (π)NAD application"

echo "✓ Service Account creado: $SA_EMAIL"

# 4. Asignar roles al Service Account
echo ""
echo "4. Asignando roles al Service Account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/documentai.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/aiplatform.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudfunctions.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudkms.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/pubsub.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/monitoring.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/logging.admin"

echo "✓ Roles asignados"

# 5. Crear clave del Service Account
echo ""
echo "5. Creando clave del Service Account..."
gcloud iam service-accounts keys create config/service_account.json \
    --iam-account=$SA_EMAIL

echo "✓ Clave creada: config/service_account.json"

# 6. Crear buckets de Cloud Storage
echo ""
echo "6. Creando buckets de Cloud Storage..."
gsutil mb -p $PROJECT_ID -l $REGION gs://${PROJECT_ID}-documents
gsutil mb -p $PROJECT_ID -l $REGION gs://${PROJECT_ID}-exports
gsutil mb -p $PROJECT_ID -l $REGION gs://${PROJECT_ID}-backups

echo "✓ Buckets creados"

# 7. Crear instancia de Cloud SQL
echo ""
echo "7. Creando instancia de Cloud SQL..."
gcloud sql instances create pinad-db \
    --project=$PROJECT_ID \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION \
    --storage-auto-increase \
    --storage-size=10GB \
    --backup-start-time=03:00

echo "✓ Instancia Cloud SQL creada"

# 8. Crear base de datos
echo ""
echo "8. Creando base de datos..."
gcloud sql databases create pinad_db --instance=pinad-db

echo "✓ Base de datos creada"

# 9. Crear usuario de base de datos
echo ""
echo "9. Creando usuario de base de datos..."
gcloud sql users create pinad_user --instance=pinad-db --password=your_secure_password

echo "✓ Usuario creado"

# 10. Crear dataset de BigQuery
echo ""
echo "10. Creando dataset de BigQuery..."
bq mk --dataset --default_partition_expiration=0 \
    --description "Dataset para (π)NAD" \
    $PROJECT_ID:pinad_analytics

echo "✓ Dataset BigQuery creado"

# 11. Crear processor de Document AI
echo ""
echo "11. Creando processor de Document AI..."
PROCESSOR_ID=$(gcloud documentai processors create \
    --project=$PROJECT_ID \
    --location=us \
    --processor-display-name="PINAD OCR Processor" \
    --processor-type="OCR_PROCESSOR" \
    --format="value(name)")

echo "✓ Processor Document AI creado: $PROCESSOR_ID"

# 12. Guardar configuración
echo ""
echo "12. Guardando configuración..."
cat > .env << EOF
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_REGION=$REGION
DOCUMENT_AI_PROCESSOR_ID=$PROCESSOR_ID
SERVICE_ACCOUNT_EMAIL=$SA_EMAIL
EOF

echo "✓ Configuración guardada en .env"

echo ""
echo "=========================================="
echo "Configuración de Google Cloud completada"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo "1. Actualizar .env con tus credenciales"
echo "2. Configurar Firebase (ver scripts/setup_firebase.sh)"
echo "3. Desplegar infraestructura con Terraform"
echo ""
echo "Service Account: $SA_EMAIL"
echo "Document AI Processor: $PROCESSOR_ID"
