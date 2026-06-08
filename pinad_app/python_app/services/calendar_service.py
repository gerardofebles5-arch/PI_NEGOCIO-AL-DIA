"""
Servicio de Google Calendar API para recordatorios
"""
import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyAG0gM9rUHowL14Aig5KrMtfdeSxnkYQik")
        self.client_id = os.getenv("GOOGLE_CLIENT_ID", "531174220363-3aeog10kkqkmbbgo21nsinf110u3qcin.apps.googleusercontent.com")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
        self.service = None
    
    def authenticate(self):
        """Autenticar con Calendar API"""
        try:
            self.service = build('calendar', 'v3', developerKey=self.api_key)
            return True
        except Exception as e:
            print(f"Error autenticando Calendar: {e}")
            return False
    
    def create_event(self, summary, description, start_time, end_time):
        """Crear evento en calendario"""
        try:
            if not self.service:
                self.authenticate()
            
            # Simulación de creación de evento
            print(f"Evento '{summary}' creado en Calendar")
            return {"id": "event_id_123", "summary": summary}
        except HttpError as error:
            print(f"Error creando evento: {error}")
            return None
    
    def create_reminder(self, document_name, due_date):
        """Crear recordatorio para documento"""
        summary = f"Vencimiento: {document_name}"
        description = f"""
        Recordatorio para documento: {document_name}
        
        Fecha de vencimiento: {due_date}
        
        (π)NAD - Sistema de Escaneo Contable
        """
        
        return self.create_event(summary, description, due_date, due_date)
    
    def create_processing_reminder(self, document_name):
        """Crear recordatorio de procesamiento"""
        from datetime import datetime, timedelta
        
        summary = f"Procesar: {document_name}"
        description = f"""
        Recordatorio para procesar documento: {document_name}
        
        Fecha: {self._get_current_date()}
        
        (π)NAD - Sistema de Escaneo Contable
        """
        
        start_time = (datetime.now() + timedelta(hours=24)).isoformat()
        end_time = (datetime.now() + timedelta(hours=25)).isoformat()
        
        return self.create_event(summary, description, start_time, end_time)
    
    def _get_current_date(self):
        """Obtener fecha actual"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
