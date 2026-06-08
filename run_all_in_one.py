"""
(π)NAD - Versión Todo en Uno
Script de ejecución unificado para demostración
"""

import sys
import os
import uuid
from datetime import datetime
from typing import Dict, List

# Añadir directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class InMemoryDatabase:
    """Base de datos en memoria para demostración"""
    
    def __init__(self):
        self.clients = {}
        self.transactions = {}
        self.documents = {}
        self.validations = {}
        self.validators = {}
    
    def add_client(self, client_data: Dict) -> Dict:
        """Agregar cliente"""
        client_id = str(uuid.uuid4())
        client_data['client_id'] = client_id
        client_data['created_at'] = datetime.now().isoformat()
        self.clients[client_id] = client_data
        return client_data
    
    def get_client(self, client_id: str) -> Dict:
        """Obtener cliente"""
        return self.clients.get(client_id)
    
    def add_transaction(self, transaction_data: Dict) -> Dict:
        """Agregar transacción"""
        transaction_id = str(uuid.uuid4())
        transaction_data['transaction_id'] = transaction_id
        transaction_data['created_at'] = datetime.now().isoformat()
        self.transactions[transaction_id] = transaction_data
        return transaction_data
    
    def add_document(self, document_data: Dict) -> Dict:
        """Agregar documento"""
        document_id = str(uuid.uuid4())
        document_data['document_id'] = document_id
        document_data['created_at'] = datetime.now().isoformat()
        self.documents[document_id] = document_data
        return document_data
    
    def add_validation(self, validation_data: Dict) -> Dict:
        """Agregar validación"""
        validation_id = str(uuid.uuid4())
        validation_data['validation_id'] = validation_id
        validation_data['created_at'] = datetime.now().isoformat()
        self.validations[validation_id] = validation_data
        return validation_data


class SimpleOCREngine:
    """Motor OCR simplificado para demostración"""
    
    def process_document(self, file_path: str, document_type: str) -> Dict:
        """Procesar documento (simulado)"""
        return {
            'success': True,
            'document_id': str(uuid.uuid4()),
            'document_type': document_type,
            'extracted_data': {
                'invoice_number': 'INV-001',
                'rif': 'J-12345678-9',
                'amount': 1000.00,
                'date': datetime.now().strftime('%Y-%m-%d')
            },
            'ocr_confidence': 0.95,
            'processing_time': 2.5
        }


class SimpleDashboardGenerator:
    """Generador de dashboard simplificado"""
    
    def generate_dashboard(self, client_id: str, transactions: List[Dict]) -> Dict:
        """Generar dashboard"""
        total_revenue = sum(t.get('amount', 0) for t in transactions)
        
        return {
            'client_id': client_id,
            'period': 'current_month',
            'summary': {
                'total_revenue': total_revenue,
                'total_expenses': total_revenue * 0.3,
                'net_income': total_revenue * 0.7,
                'transaction_count': len(transactions)
            },
            'charts': {
                'revenue_trend': [1000, 1500, 1200, 1800, 2000],
                'expense_distribution': {'operating': 30, 'taxes': 20, 'other': 50}
            },
            'generated_at': datetime.now().isoformat()
        }


class PINADAllInOne:
    """Sistema (π)NAD Todo en Uno"""
    
    def __init__(self):
        """Inicializar sistema"""
        self.db = InMemoryDatabase()
        self.ocr = SimpleOCREngine()
        self.dashboard = SimpleDashboardGenerator()
        self.current_client = None
    
    def register_client(self, rif: str, name: str, email: str, sector: str, plan: str = 'basic') -> Dict:
        """Registrar cliente"""
        client_data = {
            'rif': rif,
            'name': name,
            'email': email,
            'sector': sector,
            'plan': plan,
            'status': 'active'
        }
        client = self.db.add_client(client_data)
        self.current_client = client
        return client
    
    def process_document(self, file_path: str, document_type: str = 'invoice') -> Dict:
        """Procesar documento"""
        if not self.current_client:
            return {'success': False, 'error': 'No hay cliente registrado'}
        
        # Procesar con OCR
        ocr_result = self.ocr.process_document(file_path, document_type)
        
        # Guardar documento
        document_data = {
            'client_id': self.current_client['client_id'],
            'file_name': os.path.basename(file_path),
            'document_type': document_type,
            'processing_status': 'completed',
            'extracted_data': ocr_result['extracted_data'],
            'ocr_confidence': ocr_result['ocr_confidence']
        }
        document = self.db.add_document(document_data)
        
        # Crear transacción
        transaction_data = {
            'client_id': self.current_client['client_id'],
            'document_id': document['document_id'],
            'type': 'sale',
            'amount': ocr_result['extracted_data']['amount'],
            'status': 'pending'
        }
        transaction = self.db.add_transaction(transaction_data)
        
        return {
            'success': True,
            'document': document,
            'transaction': transaction
        }
    
    def validate_transaction(self, transaction_id: str, action: str = 'approve') -> Dict:
        """Validar transacción"""
        transaction = self.db.transactions.get(transaction_id)
        if not transaction:
            return {'success': False, 'error': 'Transacción no encontrada'}
        
        # Actualizar estado
        transaction['status'] = action
        transaction['validated_at'] = datetime.now().isoformat()
        
        # Crear registro de validación
        validation_data = {
            'transaction_id': transaction_id,
            'client_id': transaction['client_id'],
            'action': action,
            'notes': f'Transacción {action} por sistema'
        }
        validation = self.db.add_validation(validation_data)
        
        return {
            'success': True,
            'validation': validation,
            'transaction': transaction
        }
    
    def generate_dashboard(self) -> Dict:
        """Generar dashboard del cliente actual"""
        if not self.current_client:
            return {'success': False, 'error': 'No hay cliente registrado'}
        
        # Obtener transacciones del cliente
        client_transactions = [
            t for t in self.db.transactions.values()
            if t['client_id'] == self.current_client['client_id']
        ]
        
        # Generar dashboard
        dashboard = self.dashboard.generate_dashboard(
            self.current_client['client_id'],
            client_transactions
        )
        
        return {
            'success': True,
            'dashboard': dashboard
        }
    
    def get_system_stats(self) -> Dict:
        """Obtener estadísticas del sistema"""
        return {
            'clients': len(self.db.clients),
            'transactions': len(self.db.transactions),
            'documents': len(self.db.documents),
            'validations': len(self.db.validations),
            'current_client': self.current_client
        }


def print_header():
    """Imprimir encabezado"""
    print("\n" + "=" * 60)
    print("(π)NAD - Tu Contabilidad en Tres Pasos")
    print("Versión Todo en Uno - Demostración")
    print("=" * 60)


def print_menu():
    """Imprimir menú"""
    print("\n--- Menú Principal ---")
    print("1. Registrar Cliente")
    print("2. Procesar Documento")
    print("3. Validar Transacción")
    print("4. Generar Dashboard")
    print("5. Ver Estadísticas del Sistema")
    print("6. Demo Automática")
    print("0. Salir")
    print()


def demo_automatica(system: PINADAllInOne):
    """Ejecutar demo automática"""
    print("\n--- Ejecutando Demo Automática ---\n")
    
    # 1. Registrar cliente
    print("1. Registrando cliente...")
    client = system.register_client(
        rif='J-12345678-9',
        name='Empresa Demo C.A.',
        email='demo@empresa.com',
        sector='comercio',
        plan='professional'
    )
    print(f"   ✓ Cliente registrado: {client['name']} ({client['rif']})")
    
    # 2. Procesar documentos
    print("\n2. Procesando documentos...")
    for i in range(3):
        result = system.process_document(f'factura_00{i+1}.pdf', 'invoice')
        print(f"   ✓ Documento {i+1} procesado: {result['document']['document_id']}")
    
    # 3. Validar transacciones
    print("\n3. Validando transacciones...")
    transactions = list(system.db.transactions.values())
    for i, transaction in enumerate(transactions):
        result = system.validate_transaction(transaction['transaction_id'], 'approve')
        print(f"   ✓ Transacción {i+1} validada: {result['validation']['validation_id']}")
    
    # 4. Generar dashboard
    print("\n4. Generando dashboard...")
    dashboard_result = system.generate_dashboard()
    if dashboard_result['success']:
        dashboard = dashboard_result['dashboard']
        print(f"   ✓ Dashboard generado:")
        print(f"     - Ingresos Totales: ${dashboard['summary']['total_revenue']:,.2f}")
        print(f"     - Gastos Totales: ${dashboard['summary']['total_expenses']:,.2f}")
        print(f"     - Ingreso Neto: ${dashboard['summary']['net_income']:,.2f}")
        print(f"     - Transacciones: {dashboard['summary']['transaction_count']}")
    
    # 5. Estadísticas finales
    print("\n5. Estadísticas del Sistema:")
    stats = system.get_system_stats()
    print(f"   - Clientes: {stats['clients']}")
    print(f"   - Transacciones: {stats['transactions']}")
    print(f"   - Documentos: {stats['documents']}")
    print(f"   - Validaciones: {stats['validations']}")
    
    print("\n--- Demo Automática Completada ---\n")


def main():
    """Función principal"""
    print_header()
    
    # Inicializar sistema
    system = PINADAllInOne()
    print("Sistema inicializado exitosamente\n")
    
    while True:
        print_menu()
        choice = input("Seleccione una opción: ")
        
        if choice == '0':
            print("\nGracias por usar (π)NAD. ¡Hasta pronto!")
            break
        
        elif choice == '1':
            print("\n--- Registrar Cliente ---")
            rif = input("RIF: ")
            name = input("Nombre/Razón Social: ")
            email = input("Email: ")
            sector = input("Sector: ")
            plan = input("Plan (basic/professional/enterprise) [basic]: ") or 'basic'
            
            client = system.register_client(rif, name, email, sector, plan)
            print(f"\n✓ Cliente registrado: {client['name']} (ID: {client['client_id']})")
        
        elif choice == '2':
            print("\n--- Procesar Documento ---")
            if not system.current_client:
                print("Error: No hay cliente registrado. Seleccione opción 1 primero.")
                continue
            
            file_path = input("Ruta del archivo (o presione Enter para simular): ") or 'simulado.pdf'
            document_type = input("Tipo de documento (invoice/report_z) [invoice]: ") or 'invoice'
            
            result = system.process_document(file_path, document_type)
            if result['success']:
                print(f"\n✓ Documento procesado: {result['document']['document_id']}")
                print(f"  - Monto extraído: ${result['transaction']['amount']:,.2f}")
                print(f"  - Confianza OCR: {result['document']['ocr_confidence']:.2%}")
            else:
                print(f"\n✗ Error: {result['error']}")
        
        elif choice == '3':
            print("\n--- Validar Transacción ---")
            transactions = list(system.db.transactions.values())
            if not transactions:
                print("Error: No hay transacciones pendientes.")
                continue
            
            print("Transacciones disponibles:")
            for i, t in enumerate(transactions):
                print(f"  {i+1}. {t['transaction_id']} - ${t['amount']:,.2f} ({t['status']})")
            
            try:
                idx = int(input("Seleccione transacción: ")) - 1
                if 0 <= idx < len(transactions):
                    transaction = transactions[idx]
                    action = input("Acción (approve/reject) [approve]: ") or 'approve'
                    result = system.validate_transaction(transaction['transaction_id'], action)
                    if result['success']:
                        print(f"\n✓ Transacción validada: {result['validation']['validation_id']}")
                        print(f"  - Acción: {result['validation']['action']}")
                else:
                    print("Selección inválida.")
            except ValueError:
                print("Error: Selección inválida.")
        
        elif choice == '4':
            print("\n--- Generar Dashboard ---")
            if not system.current_client:
                print("Error: No hay cliente registrado. Seleccione opción 1 primero.")
                continue
            
            result = system.generate_dashboard()
            if result['success']:
                dashboard = result['dashboard']
                print(f"\n✓ Dashboard generado para {system.current_client['name']}")
                print(f"\nResumen:")
                print(f"  - Ingresos Totales: ${dashboard['summary']['total_revenue']:,.2f}")
                print(f"  - Gastos Totales: ${dashboard['summary']['total_expenses']:,.2f}")
                print(f"  - Ingreso Neto: ${dashboard['summary']['net_income']:,.2f}")
                print(f"  - Transacciones: {dashboard['summary']['transaction_count']}")
                print(f"\nGráficos:")
                print(f"  - Tendencia de Ingresos: {dashboard['charts']['revenue_trend']}")
                print(f"  - Distribución de Gastos: {dashboard['charts']['expense_distribution']}")
            else:
                print(f"\n✗ Error: {result['error']}")
        
        elif choice == '5':
            print("\n--- Estadísticas del Sistema ---")
            stats = system.get_system_stats()
            print(f"\nEstadísticas Actuales:")
            print(f"  - Clientes: {stats['clients']}")
            print(f"  - Transacciones: {stats['transactions']}")
            print(f"  - Documentos: {stats['documents']}")
            print(f"  - Validaciones: {stats['validations']}")
            if stats['current_client']:
                print(f"  - Cliente Actual: {stats['current_client']['name']}")
        
        elif choice == '6':
            demo_automatica(system)
        
        else:
            print("Opción inválida. Por favor seleccione una opción válida.")


if __name__ == '__main__':
    main()
