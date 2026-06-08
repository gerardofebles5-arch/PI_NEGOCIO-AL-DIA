"""
Script de demostración para (π)NAD
Muestra el flujo completo del sistema
"""

import os
import sys

# Añadir directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import PINADSystem
from datetime import datetime


def demo_basic_workflow():
    """Demo del flujo básico de (π)NAD"""
    print("=" * 60)
    print("(π)NAD - Demo del Flujo Básico")
    print("=" * 60)
    
    # Inicializar sistema
    print("\n1. Inicializando sistema...")
    system = PINADSystem()
    
    # Mostrar estado del sistema
    print("\n2. Estado del sistema:")
    status = system.get_system_status()
    print(f"   Inicializado: {status['initialized']}")
    print(f"   Componentes activos: {sum(status['components'].values())}/{len(status['components'])}")
    
    # Registrar cliente de prueba
    print("\n3. Registrando cliente de prueba...")
    client_data = {
        'rif': 'J-12345678-9',
        'name': 'Empresa Demo C.A.',
        'email': 'demo@empresa.com',
        'phone': '+58-414-123-4567',
        'sector': 'comercio',
        'plan': 'professional'
    }
    
    client = system.register_client(client_data)
    print(f"   Cliente registrado: {client['client_id']}")
    print(f"   Nombre: {client['name']}")
    print(f"   Plan: {client['plan']}")
    
    # Simular procesamiento de documentos
    print("\n4. Simulando procesamiento de documentos...")
    print("   (En producción, aquí se procesarían archivos reales)")
    
    # Crear solicitud de validación
    print("\n5. Creando solicitud de validación...")
    print("   (En producción, aquí se crearía solicitud para asesor)")
    
    # Generar dashboard
    print("\n6. Generando dashboard...")
    print("   (En producción, aquí se generarían métricas financieras)")
    
    print("\n" + "=" * 60)
    print("Demo completado exitosamente")
    print("=" * 60)


def demo_ocr_engine():
    """Demo del motor OCR"""
    print("=" * 60)
    print("(π)NAD - Demo del Motor OCR")
    print("=" * 60)
    
    from src.ocr.ocr_engine import OCREngine
    
    print("\n1. Inicializando motor OCR...")
    ocr_engine = OCREngine()
    
    print("\n2. Funciones disponibles:")
    print("   - extract_text(): Extraer texto de imagen")
    print("   - extract_text_with_confidence(): Extraer con confianza")
    print("   - extract_text_only(): Extraer solo texto")
    print("   - extract_invoice_data(): Extraer datos de factura")
    print("   - extract_report_z_data(): Extraer datos de Reporte Z")
    print("   - extract_from_pdf(): Extraer de PDF")
    
    print("\n3. Para probar con archivos reales:")
    print("   ocr_engine.extract_text('ruta/a/imagen.jpg')")
    print("   ocr_engine.extract_invoice_data('ruta/a/factura.jpg')")
    print("   ocr_engine.extract_report_z_data('ruta/a/reporte_z.jpg')")
    
    print("\n" + "=" * 60)
    print("Demo OCR completado")
    print("=" * 60)


def demo_api():
    """Demo de la API REST"""
    print("=" * 60)
    print("(π)NAD - Demo de API REST")
    print("=" * 60)
    
    from src.api.rest_api import create_api
    
    print("\n1. Inicializando sistema...")
    system = PINADSystem()
    
    print("\n2. Creando API...")
    api = create_api(system)
    
    print("\n3. Endpoints disponibles:")
    print("   GET  /api/v1/health - Health check")
    print("   GET  /api/v1/system/status - Estado del sistema")
    print("   POST /api/v1/clients - Crear cliente")
    print("   GET  /api/v1/clients/<id> - Obtener cliente")
    print("   GET  /api/v1/clients - Listar clientes")
    print("   POST /api/v1/documents/process - Procesar documentos")
    print("   GET  /api/v1/documents/<id> - Obtener documento")
    print("   POST /api/v1/validation/request - Crear validación")
    print("   POST /api/v1/validation/<id> - Validar transacción")
    print("   GET  /api/v1/clients/<id>/dashboard - Obtener dashboard")
    print("   POST /api/v1/dashboard/export - Exportar dashboard")
    print("   POST /api/v1/validators - Registrar asesor")
    print("   GET  /api/v1/validators/<id>/pending - Validaciones pendientes")
    print("   GET  /api/v1/validators/<id>/stats - Estadísticas de asesor")
    
    print("\n4. Para iniciar el servidor:")
    print("   api.run(host='0.0.0.0', port=5000)")
    
    print("\n" + "=" * 60)
    print("Demo API completado")
    print("=" * 60)


def demo_integrations():
    """Demo de integraciones de Google"""
    print("=" * 60)
    print("(π)NAD - Demo de Integraciones Google")
    print("=" * 60)
    
    print("\n1. Integraciones disponibles:")
    print("   - Google Forms: Creación de formularios para captura de datos")
    print("   - Google Sheets: Base de datos centralizada")
    print("   - Google Drive: Almacenamiento de archivos")
    print("   - Gmail OAuth: Autenticación segura")
    
    print("\n2. Para probar integraciones:")
    print("   from src.integrations import GoogleFormsIntegration")
    print("   from src.integrations import GoogleSheetsIntegration")
    print("   from src.integrations import GoogleDriveIntegration")
    print("   from src.auth import GmailOAuth")
    
    print("\n3. Requisitos:")
    print("   - Credenciales de Google Cloud Project")
    print("   - Service account con permisos")
    print("   - OAuth 2.0 configurado")
    
    print("\n" + "=" * 60)
    print("Demo integraciones completado")
    print("=" * 60)


def main():
    """Función principal del demo"""
    print("\nSeleccione el demo que desea ejecutar:")
    print("1. Flujo básico del sistema")
    print("2. Motor OCR")
    print("3. API REST")
    print("4. Integraciones Google")
    print("5. Ejecutar todos los demos")
    
    choice = input("\nIngrese su elección (1-5): ")
    
    if choice == '1':
        demo_basic_workflow()
    elif choice == '2':
        demo_ocr_engine()
    elif choice == '3':
        demo_api()
    elif choice == '4':
        demo_integrations()
    elif choice == '5':
        demo_basic_workflow()
        print("\n")
        demo_ocr_engine()
        print("\n")
        demo_api()
        print("\n")
        demo_integrations()
    else:
        print("Opción no válida")


if __name__ == '__main__':
    main()
