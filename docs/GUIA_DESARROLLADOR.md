# Guía de Desarrollador - (π)NAD V6.0

## Estructura del Proyecto

```
D:\NAD\
├── cloud_functions/          # Cloud Functions de Google Cloud
│   ├── python_functions/     # Funciones en Python
│   └── functions/            # Funciones en Node.js
├── pinad_app/                # Aplicación Flutter
│   ├── lib/
│   │   ├── core/             # Núcleo de la app
│   │   ├── domain/           # Capa de dominio (Clean Architecture)
│   │   ├── data/             # Capa de datos (Clean Architecture)
│   │   └── presentation/     # Capa de presentación
│   └── assets/              # Recursos estáticos
├── src/                      # Código fuente backend
│   ├── accounting/          # Módulo de contabilidad
│   ├── api/                 # API REST
│   ├── auth/                # Autenticación (OAuth2)
│   ├── monitoring/          # Monitoreo y logging
│   ├── multi_tenancy/       # Multi-tenancy
│   └── ocr/                 # Motor OCR
├── terraform/               # Configuración de infraestructura
│   ├── api_gateway.tf
│   ├── cloud_run.tf
│   ├── cloudbuild.yaml
│   └── variables.tf
├── tests/                   # Tests
│   ├── integration/         # Tests de integración
│   └── e2e/                # Tests E2E
└── docs/                    # Documentación
```

## Configuración del Entorno de Desarrollo

### 1. Clonar el Repositorio

```bash
git clone https://github.com/pinad/nad.git
cd nad
```

### 2. Configurar Python Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Configurar Flutter

```bash
cd pinad_app
flutter pub get
flutter doctor
```

### 4. Configurar Variables de Entorno

Crear archivo `.env`:

```env
DATABASE_URL=postgresql://localhost:5432/pinad
FIREBASE_PROJECT_ID=your-firebase-project-id
API_KEY=your-api-key
SECRET_KEY=your-secret-key
```

## Desarrollo Local

### 1. Ejecutar Backend

```bash
cd D:\NAD
python main.py
```

La API estará disponible en `http://localhost:5000`

### 2. Ejecutar Flutter App

```bash
cd D:\NAD\pinad_app
flutter run
```

### 3. Ejecutar Tests

```bash
# Tests unitarios
pytest tests/unit/

# Tests de integración
pytest tests/integration/

# Tests E2E
pytest tests/e2e/
```

## Convenciones de Código

### Python

- Usar type hints
- Seguir PEP 8
- Docstrings para funciones y clases
- Logging estructurado

```python
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def process_document(
    document_id: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Procesar documento con OCR
    
    Args:
        document_id: ID del documento
        options: Opciones de procesamiento
        
    Returns:
        Datos extraídos del documento
    """
    logger.info(f"Procesando documento: {document_id}")
    # ...
```

### Flutter

- Usar Clean Architecture
- BLoC/Cubit para state management
- Widgets reutilizables
- Tests para cada componente

```dart
class DocumentCubit extends Cubit<DocumentState> {
  final DocumentRepository repository;
  
  DocumentCubit(this.repository) : super(DocumentInitial());
  
  Future<void> loadDocuments() async {
    emit(DocumentLoading());
    try {
      final documents = await repository.getDocuments();
      emit(DocumentsLoaded(documents));
    } catch (e) {
      emit(DocumentError(e.toString()));
    }
  }
}
```

## Flujo de Trabajo

### 1. Crear Nueva Feature

1. Crear branch desde `main`
2. Implementar feature
3. Escribir tests
4. Ejecutar tests
5. Crear Pull Request
6. Code review
7. Merge a `main`

### 2. Code Review Checklist

- [ ] Código sigue convenciones
- [ ] Tests pasan
- [ ] No hay hardcoded values
- [ ] Logging estructurado
- [ ] Manejo de errores
- [ ] Documentación actualizada

## Debugging

### Backend

```bash
# Habilitar modo debug
export DEBUG=True
python main.py
```

### Flutter

```bash
# Ejecutar en modo debug
flutter run --debug

# Ver logs
flutter logs
```

## Recursos

- [Documentación de Google Cloud](https://cloud.google.com/docs)
- [Documentación de Flutter](https://flutter.dev/docs)
- [Documentación de Terraform](https://www.terraform.io/docs)
