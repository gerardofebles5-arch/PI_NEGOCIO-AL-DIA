"""
Script de configuración inicial para (π)NAD
"""

import os
import sys
import json
from pathlib import Path


def create_config_file():
    """Crear archivo de configuración"""
    print("Creando archivo de configuración...")
    
    config_template = """
# Configuración de Google Cloud
GOOGLE_CLOUD_PROJECT=pinad-production
GOOGLE_CLOUD_REGION=us-central1

# Configuración de OAuth
OAUTH_CLIENT_ID=your_client_id_here
OAUTH_CLIENT_SECRET=your_client_secret_here
OAUTH_REDIRECT_URI=http://localhost:5000/callback

# Configuración de Google Sheets
SHEETS_ID=your_sheets_id_here

# Configuración de Google Drive
DRIVE_FOLDER_ID=your_drive_folder_id_here

# Configuración de Document AI
DOCUMENT_AI_LOCATION=us
DOCUMENT_AI_PROCESSOR_ID=your_processor_id_here

# Configuración de Base de Datos
CLOUD_SQL_CONNECTION_NAME=your_connection_name_here
DB_USER=pinad_user
DB_PASSWORD=your_password_here
DB_NAME=pinad_db
DB_HOST=localhost
DB_PORT=5432

# Configuración de API
API_BASE_URL=http://localhost:5000
API_KEY=your_api_key_here

# Configuración de Logging
LOG_LEVEL=INFO
LOG_FILE=logs/pinad.log
"""
    
    with open('.env', 'w') as f:
        f.write(config_template.strip())
    
    print("✓ Archivo .env creado")


def create_service_account_template():
    """Crear plantilla para credenciales de service account"""
    print("Creando plantilla de credenciales...")
    
    # Crear directorio config si no existe
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)
    
    # Crear archivo README para credenciales
    readme_content = """
# Credenciales de Google Cloud

Para configurar las credenciales de Google Cloud:

1. Ve a Google Cloud Console
2. Crea un Service Account
3. Descarga el archivo JSON de credenciales
4. Renómbralo a 'service_account.json'
5. Colócalo en este directorio (config/)

El archivo debe tener el siguiente formato:
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
"""
    
    with open('config/README.md', 'w') as f:
        f.write(readme_content.strip())
    
    print("✓ Plantilla de credenciales creada")


def create_oauth_credentials_template():
    """Crear plantilla para credenciales OAuth"""
    print("Creando plantilla de credenciales OAuth...")
    
    oauth_template = {
        "client_id": "your_oauth_client_id_here",
        "client_secret": "your_oauth_client_secret_here",
        "redirect_uri": "http://localhost:5000/callback"
    }
    
    with open('config/oauth_credentials.json', 'w') as f:
        json.dump(oauth_template, f, indent=2)
    
    print("✓ Plantilla de credenciales OAuth creada")


def create_directories():
    """Crear directorios necesarios"""
    print("Creando directorios necesarios...")
    
    directories = [
        'logs',
        'uploads',
        'temp',
        'exports'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Directorio {directory}/ creado")


def check_dependencies():
    """Verificar dependencias instaladas"""
    print("Verificando dependencias...")
    
    required_packages = [
        'flask',
        'easyocr',
        'opencv-python',
        'google-api-python-client',
        'google-auth',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} instalado")
        except ImportError:
            print(f"✗ {package} NO instalado")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nPaquetes faltantes: {', '.join(missing_packages)}")
        print("Instala con: pip install -r requirements.txt")
        return False
    else:
        print("\nTodas las dependencias están instaladas")
        return True


def create_initial_setup_script():
    """Crear script de configuración inicial"""
    print("Creando script de configuración inicial...")
    
    setup_script = """
#!/bin/bash
# Script de configuración inicial para (π)NAD

echo "Configurando (π)NAD..."

# Crear directorios
mkdir -p logs uploads temp exports config

# Crear archivo .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Archivo .env creado. Por favor, configúralo con tus credenciales."
fi

# Instalar dependencias
pip install -r requirements.txt

echo "Configuración inicial completada."
echo "Por favor:"
echo "1. Configura el archivo .env con tus credenciales"
echo "2. Coloca el archivo service_account.json en config/"
echo "3. Ejecuta python main.py para iniciar el sistema"
"""
    
    with open('setup.sh', 'w') as f:
        f.write(setup_script.strip())
    
    # Hacer ejecutable en Unix/Linux/Mac
    try:
        os.chmod('setup.sh', 0o755)
        print("✓ Script setup.sh creado")
    except:
        print("✓ Script setup.sh creado (no se pudo hacer ejecutable en Windows)")


def create_gitignore():
    """Crear archivo .gitignore"""
    print("Creando archivo .gitignore...")
    
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Configuración y credenciales
.env
config/service_account.json
config/oauth_credentials.json
*.key

# Logs
logs/
*.log

# Archivos temporales
temp/
uploads/
exports/

# OS
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    
    print("✓ Archivo .gitignore creado")


def main():
    """Función principal de configuración"""
    print("=" * 60)
    print("(π)NAD - Configuración Inicial")
    print("=" * 60)
    print()
    
    # Crear directorios
    create_directories()
    print()
    
    # Crear archivos de configuración
    create_config_file()
    print()
    
    create_service_account_template()
    print()
    
    create_oauth_credentials_template()
    print()
    
    create_gitignore()
    print()
    
    create_initial_setup_script()
    print()
    
    # Verificar dependencias
    dependencies_ok = check_dependencies()
    print()
    
    print("=" * 60)
    print("Configuración inicial completada")
    print("=" * 60)
    print()
    print("Próximos pasos:")
    print("1. Configura el archivo .env con tus credenciales")
    print("2. Coloca el archivo service_account.json en config/")
    print("3. Configura las credenciales OAuth en config/oauth_credentials.json")
    print("4. Ejecuta 'python main.py' para iniciar el sistema")
    print("5. Ejecuta 'python demo.py' para ver el demo")
    
    if not dependencies_ok:
        print()
        print("IMPORTANTE: Instala las dependencias con:")
        print("pip install -r requirements.txt")


if __name__ == '__main__':
    main()
