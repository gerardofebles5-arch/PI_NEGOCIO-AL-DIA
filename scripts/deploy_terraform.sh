#!/bin/bash
# Script para desplegar infraestructura con Terraform

set -e

echo "=========================================="
echo "(π)NAD V6.0 - Terraform Deployment"
echo "=========================================="

cd terraform

# 1. Inicializar Terraform
echo ""
echo "1. Inicializando Terraform..."
terraform init

echo "✓ Terraform inicializado"

# 2. Validar configuración
echo ""
echo "2. Validando configuración..."
terraform validate

echo "✓ Configuración válida"

# 3. Planificar despliegue
echo ""
echo "3. Planificando despliegue..."
terraform plan -out=tfplan

echo "✓ Plan creado"

# 4. Aplicar despliegue
echo ""
echo "4. Aplicando despliegue..."
terraform apply tfplan

echo "✓ Infraestructura desplegada"

# 5. Mostrar outputs
echo ""
echo "5. Mostrando outputs..."
terraform output

echo ""
echo "=========================================="
echo "Despliegue completado"
echo "=========================================="
