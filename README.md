# (π)NAD — Web app

Aplicación web **100% gratuita** para **escanear documentos e imágenes**, **extraer
su información** automáticamente y archivarla en una base de datos, con un
**dashboard inteligente** y autenticación con **Google**.

## Funcionalidades

1. **Escaneo y extracción** de documentos: PDF, imágenes/fotos (OCR), Word
   (`.docx`), PowerPoint (`.pptx`), Excel/CSV y texto. Se detectan automáticamente
   montos, monedas, fechas, correos, teléfonos, RIF y palabras clave.
2. **Login con Google** (Google Identity Services) + registro automático del usuario.
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
- **Auth**: Google Identity Services (solo requiere el *Client ID* público).

## Estructura

```
backend/            # API FastAPI
  app/
    main.py         # app + monta el frontend compilado
    config.py       # configuración por variables de entorno
    database.py     # SQLAlchemy + SQLite
    models.py       # User, Document, Extraction
    auth.py         # Google + JWT de sesión + roles
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
cp .env.example .env        # ajusta GOOGLE_CLIENT_ID, JWT_SECRET, etc.
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173 (proxy /api -> :8000)
```

Mientras no haya `GOOGLE_CLIENT_ID` configurado, la pantalla de login ofrece un
**acceso de prueba** (solo desarrollo) para poder usar la app.

## Configurar Google (gratis)

1. Google Cloud Console → **APIs & Services → Credentials → Create credentials →
   OAuth client ID**.
2. Tipo **Web application**.
3. **Authorized JavaScript origins**: la URL donde corre la app
   (ej. `http://localhost:5173` y tu dominio de producción).
4. Copia el **Client ID** en `GOOGLE_CLIENT_ID` (variable de entorno del backend).

> Con Google Identity Services solo se necesita el **Client ID** (público) para
> verificar el inicio de sesión; no hace falta el Client Secret.

## Despliegue (Docker)

El `Dockerfile` compila el frontend, instala Tesseract y sirve todo desde FastAPI
en un solo contenedor. Define `GOOGLE_CLIENT_ID`, `JWT_SECRET` y `ALLOW_DEV_LOGIN=false`
en producción, y monta un volumen en `/app/data` para persistir la base de datos.
