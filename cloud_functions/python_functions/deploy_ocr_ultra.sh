#!/bin/bash

# Script para desplegar la Cloud Function de OCR Ultra Avanzado

PROJECT_ID="pinad-project"
REGION="us-central1"
FUNCTION_NAME="process_document_ultra"
ENTRY_POINT="process_document_ultra"
RUNTIME="python310"
SOURCE="."

echo "Desplegando Cloud Function: $FUNCTION_NAME"
echo "Proyecto: $PROJECT_ID"
echo "Región: $REGION"
echo "Runtime: $RUNTIME"

# Desplegar la Cloud Function
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=$RUNTIME \
  --region=$REGION \
  --source=$SOURCE \
  --entry-point=$ENTRY_POINT \
  --trigger-http \
  --allow-unauthenticated \
  --memory=512MB \
  --timeout=60s \
  --max-instances=10 \
  --project=$PROJECT_ID

echo "Cloud Function desplegada exitosamente"
