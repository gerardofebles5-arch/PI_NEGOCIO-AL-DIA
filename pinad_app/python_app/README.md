# (π)NAD - Sistema de Escaneo Contable

Aplicación web en Python con Streamlit para gestión de documentos contables e integración con Google Workspace.

## Características

- **Dashboard General**: Métricas y visualización de documentos procesados
- **Gestión de Documentos**: Upload y procesamiento de documentos
- **Reportes**: Generación de reportes IVA, ISLR, Balance General
- **Integración Google Workspace**:
  - Gmail: Notificaciones por email
  - Drive: Backup de documentos
  - Sheets: Generación de reportes
  - Calendar: Recordatorios de vencimientos

## Instalación Local

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```

## Configuración

Copiar `.env.example` a `.env` y configurar las credenciales de Google:

```bash
cp .env.example .env
```

Variables de entorno requeridas:
- `GOOGLE_API_KEY`: API Key de Google
- `GOOGLE_CLIENT_ID`: Client ID de OAuth 2.0
- `GOOGLE_CLIENT_SECRET`: Client Secret de OAuth 2.0
- `GMAIL_NOTIFICATION_EMAIL`: Email para notificaciones
- `DRIVE_BACKUP_FOLDER`: Carpeta de backup en Drive
- `SHEETS_REPORT_FOLDER`: Carpeta de reportes en Sheets
- `CALENDAR_REMINDER_CALENDAR`: Calendario de recordatorios

## Despliegue en Render

1. Crear cuenta en [Render](https://render.com)
2. Crear nuevo Web Service
3. Conectar repositorio GitHub
4. Configurar variables de entorno
5. Deploy automático

## Servicios de Google

### Gmail API
- Envío de notificaciones de documentos procesados
- Alertas de vencimientos
- Reportes por email

### Drive API
- Backup automático de documentos
- Organización por carpetas
- Control de versiones

### Sheets API
- Generación de reportes IVA
- Generación de reportes ISLR
- Balance general
- Estado de resultados

### Calendar API
- Recordatorios de vencimientos
- Alertas de procesamiento
- Programación de tareas

## Estructura del Proyecto

```
python_app/
├── app.py                 # Aplicación principal Streamlit
├── requirements.txt        # Dependencias Python
├── render.yaml            # Configuración de Render
├── .env.example           # Variables de entorno ejemplo
├── services/              # Servicios de Google
│   ├── __init__.py
│   ├── gmail_service.py
│   ├── drive_service.py
│   ├── sheets_service.py
│   └── calendar_service.py
└── README.md              # Este archivo
```

## Uso

1. Abrir aplicación en navegador
2. Navegar entre Dashboard, Documentos, Reportes, Configuración
3. Subir documentos para procesar
4. Generar reportes automáticos
5. Configurar integraciones con Google

## Notas

- La aplicación usa credenciales de Google preconfiguradas
- Los servicios de Google están en modo simulación por defecto
- Para producción, configurar OAuth 2.0 completo
- La base de datos usa SQLite por defecto (puede cambiar a PostgreSQL)
