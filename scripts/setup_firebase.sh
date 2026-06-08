#!/bin/bash
# Script para configurar Firebase Project para (π)NAD V6.0

set -e

echo "=========================================="
echo "(π)NAD V6.0 - Firebase Setup"
echo "=========================================="

# Variables
PROJECT_ID=${FIREBASE_PROJECT_ID:-"your-firebase-project-id"}

echo "Configurando Firebase Project: $PROJECT_ID"

# 1. Instalar Firebase CLI
echo ""
echo "1. Verificando Firebase CLI..."
if ! command -v firebase &> /dev/null; then
    echo "Firebase CLI no encontrado. Instalando..."
    npm install -g firebase-tools
else
    echo "✓ Firebase CLI ya instalado"
fi

# 2. Login en Firebase
echo ""
echo "2. Login en Firebase..."
firebase login

# 3. Crear proyecto Firebase
echo ""
echo "3. Creando proyecto Firebase..."
firebase projects:create $PROJECT_ID

echo "✓ Proyecto Firebase creado: $PROJECT_ID"

# 4. Habilitar Authentication
echo ""
echo "4. Habilitando Authentication..."
firebase auth:enable

# Habilitar Email/Password
firebase auth:provider create email

# Habilitar Google Sign-In
firebase auth:provider create google

echo "✓ Authentication habilitado"

# 5. Habilitar Cloud Messaging
echo ""
echo "6. Habilitando Cloud Messaging..."
firebase messaging:enable

echo "✓ Cloud Messaging habilitado"

# 6. Habilitar Analytics
echo ""
echo "7. Habilitando Analytics..."
firebase analytics:enable

echo "✓ Analytics habilitado"

# 7. Habilitar Crashlytics
echo ""
echo "8. Habilitando Crashlytics..."
firebase crashlytics:enable

echo "✓ Crashlytics habilitado"

# 8. Habilitar Performance Monitoring
echo ""
echo "9. Habilitando Performance Monitoring..."
firebase performance:enable

echo "✓ Performance Monitoring habilitado"

# 9. Configurar Flutter
echo ""
echo "10. Configurando Flutter con Firebase..."
cd pinad_app

flutterfire configure \
    --project=$PROJECT_ID \
    --platforms=android,ios,web

echo "✓ Flutter configurado con Firebase"

# 11. Obtener configuración de Firebase
echo ""
echo "11. Obteniendo configuración de Firebase..."
firebase projects:list

# Guardar configuración
cat > ../.env << EOF
FIREBASE_PROJECT_ID=$PROJECT_ID
EOF

echo "✓ Configuración guardada en .env"

echo ""
echo "=========================================="
echo "Configuración de Firebase completada"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo "1. Copiar google-services.json a pinad_app/android/app/"
echo "2. Copiar GoogleService-Info.plist a pinad_app/ios/Runner/"
echo "3. Ejecutar flutter pub get"
echo "4. Ejecutar flutter run"
