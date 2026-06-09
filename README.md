# (π)NAD — Web app

Aplicación web **100% gratuita** para **escanear documentos e imágenes**, **extraer
su información** automáticamente y archivarla en una base de datos, con un
**dashboard inteligente** y registro de usuarios con **correo + contraseña** y
**verificación por código** enviado al email.

## Funcionalidades

1. **Escaneo y extracción** de documentos: PDF, imágenes/fotos (OCR), Word
   (`.docx`), PowerPoint (`.pptx`), Excel/CSV y texto. Se detectan automáticamente
   montos, monedas, fechas, correos, teléfonos, RIF y palabras clave.
2. **Registro con correo + contraseña** y **verificación por código** (enviado por
   email vía SMTP). Sin servicios de pago ni Google Cloud.
3. **Base de datos**: usuarios y datos extraídos quedan guardados y archivados para
   uso posterior.
4. **Dashboard inteligente** que reacciona a la información de cada usuario
   (resumen, gráficos e insights).
5. **Dos niveles de usuario**:
   - **ADMIN** (`gerardofebles5@gmail.com`, `gfebles@negocioaldia.app`): acceso a
     toda la información (usuarios y documentos).
   - **Usuario**: acceso solo a su propio perfil y sus documentos.
6. **Responsive** y con **escaneo por la cámara del teléfono**.

## Stack (todo open-source / gratuito)

- **Frontend**: React + Vite + TypeScript + Tailwind CSS (identidad visual Pi NAD).
- **Backend**: FastAPI (Python) + SQLAlchemy.
- **Base de datos**: SQLite (sin costo; portable a PostgreSQL cambiando `DATABASE_URL`).
- **OCR**: Tesseract (`pytesseract`). Parsers: `pdfplumber`, `PyMuPDF`,
  `python-docx`, `python-pptx`, `openpyxl`.
- **Auth**: correo + contraseña (hash PBKDF2), sesión JWT y verificación por código
  enviado por email (SMTP gratuito, p. ej. Gmail con *contraseña de aplicación*).

## Estructura

```
backend/            # API FastAPI
  app/
    main.py         # app + monta el frontend compilado
    config.py       # configuración por variables de entorno
    database.py     # SQLAlchemy + SQLite
    models.py       # User, Document, Extraction
    auth.py         # contraseñas (PBKDF2) + JWT de sesión + roles
    email_utils.py  # envío del código de verificación por SMTP
    extraction.py   # extracción de texto + campos estructurados
    routers/        # auth, documents, dashboard, admin
frontend/           # React + Vite + Tailwind
Dockerfile          # build del frontend + backend + Tesseract
```

## Desarrollo local

Requisitos: Python 3.11+, Node 20+. (OCR de imágenes requiere el binario de
Tesseract instalado; sin él, la extracción de texto de PDF/Word/Excel/etc. sigue
funcionando.)

### Backend
```bash
cd backend
python -m pip install -r requirements.txt
cp .env.example .env        # ajusta SMTP_*, JWT_SECRET, ADMIN_EMAILS, etc.
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173 (proxy /api -> :8000)
```

Si no configuras SMTP, la app sigue funcionando en desarrollo: el código de
verificación se imprime en los **logs del servidor** en lugar de enviarse por email.

## Configurar el envío de correos (gratis, con Gmail)

1. Activa la verificación en dos pasos en tu cuenta de Google.
2. Crea una **contraseña de aplicación**: https://myaccount.google.com/apppasswords
3. Rellena en `.env`:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=tu-correo@gmail.com
   SMTP_PASSWORD=la-contraseña-de-aplicación
   SMTP_USE_TLS=true
   ```

> No requiere Google Cloud ni facturación: una *contraseña de aplicación* de Gmail
> es gratuita. También sirve cualquier otro SMTP gratuito.

## Despliegue (Docker)

El `Dockerfile` compila el frontend, instala Tesseract y sirve todo desde FastAPI
en un solo contenedor. Define `JWT_SECRET`, `ADMIN_EMAILS` y las variables `SMTP_*`
en producción, y monta un volumen en `/app/data` para persistir la base de datos.
