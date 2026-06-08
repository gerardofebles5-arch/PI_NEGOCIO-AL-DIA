"""
Módulo de autenticación Gmail OAuth para (π)NAD
"""

from google.oauth2 import flow
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from flask import Flask, request, redirect, session, jsonify
import secrets
import json
from typing import Dict, Optional
import os


class GmailOAuth:
    """Sistema de autenticación Gmail OAuth para (π)NAD"""
    
    def __init__(self, client_id: str = None, client_secret: str = None, 
                 redirect_uri: str = None):
        """
        Inicializar sistema de autenticación OAuth
        
        Args:
            client_id: Client ID de Google OAuth
            client_secret: Client Secret de Google OAuth
            redirect_uri: URI de redirección para OAuth callback
        """
        self.client_id = client_id or os.getenv('OAUTH_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('OAUTH_CLIENT_SECRET')
        self.redirect_uri = redirect_uri or os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:5000/callback')
        
        self.scopes = [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/gmail.readonly'
        ]
        
        self.app = Flask(__name__)
        self.app.secret_key = secrets.token_hex(32)
        self._setup_routes()
    
    def _setup_routes(self):
        """Configurar rutas de Flask para OAuth"""
        
        @self.app.route('/login')
        def login():
            """Iniciar flujo OAuth"""
            return self._login_handler()
        
        @self.app.route('/callback')
        def callback():
            """Callback de OAuth"""
            return self._callback_handler()
        
        @self.app.route('/userinfo')
        def userinfo():
            """Obtener información del usuario"""
            return self._userinfo_handler()
        
        @self.app.route('/logout')
        def logout():
            """Cerrar sesión"""
            return self._logout_handler()
    
    def _login_handler(self):
        """Manejador de login"""
        oauth_flow = flow.Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        # Generar state para seguridad
        state = secrets.token_urlsafe(16)
        session['oauth_state'] = state
        
        # Generar URL de autorización
        authorization_url, state = oauth_flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'
        )
        
        return redirect(authorization_url)
    
    def _callback_handler(self):
        """Manejador de callback"""
        # Verificar state
        state = request.args.get('state')
        if state != session.get('oauth_state'):
            return 'Error: Invalid state', 400
        
        # Crear flujo OAuth
        oauth_flow = flow.Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri,
            state=state
        )
        
        # Intercambiar authorization code por tokens
        authorization_response = request.url
        oauth_flow.fetch_token(authorization_response=authorization_response)
        
        # Guardar credenciales en sesión
        credentials = oauth_flow.credentials
        session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Obtener información del usuario
        userinfo = self._get_userinfo(credentials.token)
        session['user_email'] = userinfo.get('email')
        session['user_name'] = userinfo.get('name')
        
        return redirect('/dashboard')
    
    def _userinfo_handler(self):
        """Manejador de userinfo"""
        if 'credentials' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        credentials_data = session['credentials']
        userinfo = self._get_userinfo(credentials_data['token'])
        
        return jsonify(userinfo)
    
    def _logout_handler(self):
        """Manejador de logout"""
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    
    def _get_userinfo(self, access_token: str) -> Dict:
        """Obtener información del usuario de Google"""
        import requests
        
        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': 'Failed to get userinfo'}
        except Exception as e:
            return {'error': str(e)}
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Ejecutar servidor Flask"""
        self.app.run(host=host, port=port, debug=debug)


class OAuthCredentialsManager:
    """Gestor de credenciales OAuth para (π)NAD"""
    
    def __init__(self, credentials_file: str = 'config/oauth_credentials.json'):
        """
        Inicializar gestor de credenciales
        
        Args:
            credentials_file: Ruta al archivo de credenciales
        """
        self.credentials_file = credentials_file
        self.credentials = self._load_credentials()
    
    def _load_credentials(self) -> Dict:
        """Cargar credenciales desde archivo"""
        try:
            with open(self.credentials_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Error cargando credenciales: {e}")
            return {}
    
    def save_credentials(self, credentials: Dict):
        """Guardar credenciales en archivo"""
        try:
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            return True
        except Exception as e:
            print(f"Error guardando credenciales: {e}")
            return False
    
    def get_client_id(self) -> Optional[str]:
        """Obtener Client ID"""
        return self.credentials.get('client_id')
    
    def get_client_secret(self) -> Optional[str]:
        """Obtener Client Secret"""
        return self.credentials.get('client_secret')
    
    def get_redirect_uri(self) -> Optional[str]:
        """Obtener Redirect URI"""
        return self.credentials.get('redirect_uri')
    
    def set_credentials(self, client_id: str, client_secret: str, redirect_uri: str):
        """Establecer credenciales"""
        self.credentials = {
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
        self.save_credentials(self.credentials)


class TokenManager:
    """Gestor de tokens OAuth para (π)NAD"""
    
    def __init__(self):
        """Inicializar gestor de tokens"""
        self.tokens = {}
    
    def save_token(self, user_id: str, token_data: Dict):
        """
        Guardar token de usuario
        
        Args:
            user_id: ID del usuario (email)
            token_data: Datos del token
        """
        self.tokens[user_id] = token_data
    
    def get_token(self, user_id: str) -> Optional[Dict]:
        """
        Obtener token de usuario
        
        Args:
            user_id: ID del usuario (email)
            
        Returns:
            Datos del token o None si no existe
        """
        return self.tokens.get(user_id)
    
    def refresh_token(self, user_id: str, client_id: str, client_secret: str) -> Optional[Dict]:
        """
        Refrescar token de usuario
        
        Args:
            user_id: ID del usuario (email)
            client_id: Client ID de OAuth
            client_secret: Client Secret de OAuth
            
        Returns:
            Nuevos datos del token o None si falla
        """
        import requests
        
        token_data = self.get_token(user_id)
        if not token_data or 'refresh_token' not in token_data:
            return None
        
        try:
            response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': token_data['refresh_token'],
                    'client_id': client_id,
                    'client_secret': client_secret
                }
            )
            
            if response.status_code == 200:
                new_token_data = response.json()
                # Actualizar token
                token_data.update({
                    'token': new_token_data['access_token'],
                    'refresh_token': new_token_data.get('refresh_token', token_data['refresh_token'])
                })
                self.save_token(user_id, token_data)
                return token_data
            else:
                return None
        except Exception as e:
            print(f"Error refrescando token: {e}")
            return None
    
    def remove_token(self, user_id: str):
        """
        Eliminar token de usuario
        
        Args:
            user_id: ID del usuario (email)
        """
        if user_id in self.tokens:
            del self.tokens[user_id]
