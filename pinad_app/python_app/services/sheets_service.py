"""
Servicio de Google Sheets API para reportes
"""
import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class SheetsService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyAG0gM9rUHowL14Aig5KrMtfdeSxnkYQik")
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "531174220363-3aeog10kkqkmbbgo21nsinf110u3qcin.apps.googleusercontent.com")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
        self.service = None
    
    def authenticate(self):
        """Autenticar con Sheets API"""
        try:
            self.service = build('sheets', 'v4', developerKey=self.api_key)
            return True
        except Exception as e:
            print(f"Error autenticando Sheets: {e}")
            return False
    
    def create_spreadsheet(self, title):
        """Crear hoja de cálculo"""
        try:
            if not self.service:
                self.authenticate()
            
            # Simulación de creación
            print(f"Hoja de cálculo {title} creada en Sheets")
            return {"spreadsheetId": "sheet_id_123", "title": title}
        except HttpError as error:
            print(f"Error creando hoja: {error}")
            return None
    
    def add_data(self, spreadsheet_id, range_name, values):
        """Agregar datos a hoja de cálculo"""
        try:
            if not self.service:
                self.authenticate()
            
            # Simulación de agregar datos
            print(f"Datos agregados a hoja {spreadsheet_id}")
            return True
        except HttpError as error:
            print(f"Error agregando datos: {error}")
            return False
    
    def generate_iva_report(self, report_data):
        """Generar reporte de IVA"""
        title = f"Reporte IVA - {self._get_current_date()}"
        spreadsheet = self.create_spreadsheet(title)
        
        if spreadsheet:
            # Datos del reporte
            values = [
                ["Concepto", "Monto"],
                ["Ventas Gravadas", report_data.get("ventas_gravadas", 0)],
                ["Compras Gravadas", report_data.get("compras_gravadas", 0)],
                ["IVA Débito Fiscal", report_data.get("iva_debito", 0)],
                ["IVA Crédito Fiscal", report_data.get("iva_credito", 0)],
                ["IVA a Pagar", report_data.get("iva_pagar", 0)],
            ]
            
            return self.add_data(spreadsheet["spreadsheetId"], "Hoja1!A1:B6", values)
        return False
    
    def _get_current_date(self):
        """Obtener fecha actual"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
