# Instrucciones de Despliegue Rápido en Render

## PASO 1: Crear Repositorio en GitHub (5 minutos)

1. Ir a https://github.com/new
2. Nombre: `pinad-python-app`
3. Hacer público
4. Copiar estos archivos al repositorio:
   - app.py
   - requirements.txt
   - render.yaml
   - services/ (todo el directorio)
   - README.md
   - .env.example

## PASO 2: Subir Código (2 minutos)

```bash
cd D:\NAD\pinad_app\python_app
git init
git add .
git commit -m "Versión final con OCR real y colores (π)NAD"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/pinad-python-app.git
git push -u origin main
```

## PASO 3: Desplegar en Render (5 minutos)

1. Ir a https://dashboard.render.com
2. Click "New" → "Web Service"
3. Conectar repositorio GitHub
4. Render detectará automáticamente el archivo render.yaml
5. Click "Deploy Web Service"
6. Esperar 2-3 minutos

## PASO 4: Configurar Variables de Entorno (2 minutos)

En Render Dashboard → pinad-python-app → Environment:

```
GOOGLE_API_KEY=AIzaSyAG0gM9rUHowL14Aig5KrMtfdeSxnkYQik
GOOGLE_CLIENT_ID=531174220363-3aeog10kkqkmbbgo21nsinf110u3qcin.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET
SUPABASE_URL=https://rteuftlsbglpgcawsdqz.supabase.co
SUPABASE_KEY=sb_publishable_eUlKRfeFNvqdURtW_abbIA_N8Qte0l3
GMAIL_NOTIFICATION_EMAIL=contador@ejemplo.com
```

## TIEMPO TOTAL: ~15 minutos

## CARACTERÍSTICAS IMPLEMENTADAS:

✅ Colores de la marca (π)NAD (#936A31, #512509, #f4e0ab)
✅ OCR real conectado a Supabase Edge Function
✅ Integración real con Gmail API
✅ Integración real con Drive API
✅ Integración real con Sheets API
✅ Integración real con Calendar API
✅ Dashboard con métricas
✅ Gestión de documentos con upload
✅ Reportes IVA e ISLR
✅ Configuración de servicios

## URL FINAL:
Después del despliegue, Render te dará una URL como:
https://pinad-python-app.onrender.com
