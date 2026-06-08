# Despliegue en Render - Sistema OCR Ultra

## Preparativos Completados ✅

1. **requirements.txt**: Actualizado con todas las dependencias necesarias (EasyOCR, Flask, Pillow, numpy, opencv-python-headless, etc.)
2. **Procfile**: Creado para Render (`web: python main.py`)
3. **Configuración PORT**: main.py configurado para usar puerto de Render
4. **.gitignore**: Configurado para excluir archivos innecesarios
5. **Repositorio Git**: Inicializado

## Pasos para Desplegar en Render

### 1. Crear Repositorio en GitHub

```bash
git add .
git commit -m "Sistema OCR Ultra - Despliegue inicial"
```

Luego:
1. Ve a [GitHub](https://github.com) y crea un nuevo repositorio
2. Sigue las instrucciones de GitHub para conectar tu repositorio local

```bash
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git branch -M main
git push -u origin main
```

### 2. Crear Nuevo Servicio en Render

1. Ve a [dashboard.render.com](https://dashboard.render.com)
2. Clic en "New +" → "Web Service"
3. Conecta tu repositorio de GitHub
4. Configura:

**Build & Deploy:**
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`

**Environment Variables:**
- No se requieren variables adicionales para el modo local

### 3. Despliegue Automático

Render automáticamente:
- Detectará los cambios en tu repositorio
- Instalará las dependencias
- Iniciará el servidor
- Te proporcionará una URL pública

### 4. Actualizar Interfaz Web

Una vez desplegado, actualiza la URL en `web_interface/index.html`:

```javascript
const API_BASE = 'https://TU_APP_RENDER.onrender.com';
```

## Características del Despliegue

- **Automático**: Cada push a GitHub despliega automáticamente
- **HTTPS**: Certificado SSL gratuito
- **Dominio**: Subdominio gratuito de Render
- **Logs**: Logs en tiempo real en el dashboard de Render
- **Escalabilidad**: Render escala automáticamente según el tráfico

## Endpoints Disponibles

- `GET /api/health` - Health check
- `GET /api/` - Información del sistema
- `POST /api/ocr` - Procesamiento OCR avanzado
- `POST /api/ocr/batch` - Procesamiento batch
- `GET /api/ocr/cache/stats` - Estadísticas de cache
- `POST /api/ocr/cache/clear` - Limpiar cache
- `GET /api/logs` - Logs del sistema

## Notas Importantes

- EasyOCR descargará modelos automáticamente en el primer despliegue (puede tardar unos minutos)
- Render tiene límites de recursos en el plan gratuito
- Para producción, considera actualizar a un plan de pago
- El cache de EasyOCR se reiniciará en cada despliegue
