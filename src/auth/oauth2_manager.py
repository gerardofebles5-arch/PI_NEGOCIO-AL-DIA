"""
OAuth2 Manager para (π)NAD V6.0
Gestor centralizado de autenticación OAuth2 con múltiples proveedores
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from .oauth2_pkce import OAuth2PKCEClient, OAuth2TokenRotationManager

logger = logging.getLogger(__name__)


class OAuth2Provider:
    """Configuración de proveedor OAuth2"""
    
    GOOGLE = {
        'name': 'Google',
        'client_id': 'google_client_id',
        'authorization_endpoint': 'https://accounts.google.com/o/oauth2/v2/auth',
        'token_endpoint': 'https://oauth2.googleapis.com/token',
        'redirect_uri': 'https://pinad.com/auth/callback/google',
        'scope': 'openid profile email',
    }
    
    MICROSOFT = {
        'name': 'Microsoft',
        'client_id': 'microsoft_client_id',
        'authorization_endpoint': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'token_endpoint': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        'redirect_uri': 'https://pinad.com/auth/callback/microsoft',
        'scope': 'openid profile email',
    }
    
    GITHUB = {
        'name': 'GitHub',
        'client_id': 'github_client_id',
        'authorization_endpoint': 'https://github.com/login/oauth/authorize',
        'token_endpoint': 'https://github.com/login/oauth/access_token',
        'redirect_uri': 'https://pinad.com/auth/callback/github',
        'scope': 'user:email',
    }


class OAuth2Manager:
    """
    Gestor centralizado de autenticación OAuth2
    Soporta múltiples proveedores y gestión de tokens
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializar gestor OAuth2
        
        Args:
            config: Configuración de OAuth2
        """
        self.config = config
        self.clients: Dict[str, OAuth2PKCEClient] = {}
        self.rotation_managers: Dict[str, OAuth2TokenRotationManager] = {}
        self.active_provider: Optional[str] = None
        
        # Inicializar clientes configurados
        self._initialize_clients()
        
        logger.info("OAuth2 Manager inicializado")
    
    def _initialize_clients(self) -> None:
        """Inicializar clientes OAuth2 configurados"""
        for provider_name, provider_config in OAuth2Provider.__dict__.items():
            if provider_name.startswith('_'):
                continue
            
            if provider_name.lower() in self.config.get('enabled_providers', []):
                client_id = self.config.get(f'{provider_name.lower()}_client_id')
                
                if client_id:
                    client = OAuth2PKCEClient(
                        client_id=client_id,
                        authorization_endpoint=provider_config['authorization_endpoint'],
                        token_endpoint=provider_config['token_endpoint'],
                        redirect_uri=provider_config['redirect_uri'],
                        scope=provider_config['scope'],
                        token_rotation_enabled=self.config.get('token_rotation_enabled', True),
                        token_expiry_buffer=self.config.get('token_expiry_buffer', 300),
                    )
                    
                    self.clients[provider_name.lower()] = client
                    self.rotation_managers[provider_name.lower()] = OAuth2TokenRotationManager(client)
                    
                    logger.info(f"Cliente OAuth2 inicializado: {provider_name}")
    
    def get_provider_client(self, provider: str) -> OAuth2PKCEClient:
        """
        Obtener cliente OAuth2 para un proveedor
        
        Args:
            provider: Nombre del proveedor
            
        Returns:
            Cliente OAuth2 PKCE
        """
        if provider not in self.clients:
            raise ValueError(f"Proveedor {provider} no configurado")
        
        return self.clients[provider]
    
    def set_active_provider(self, provider: str) -> None:
        """
        Establecer proveedor activo
        
        Args:
            provider: Nombre del proveedor
        """
        if provider not in self.clients:
            raise ValueError(f"Proveedor {provider} no configurado")
        
        self.active_provider = provider
        logger.info(f"Proveedor activo establecido: {provider}")
    
    def get_authorization_url(self, provider: Optional[str] = None) -> str:
        """
        Generar URL de autorización
        
        Args:
            provider: Nombre del proveedor (default: activo)
            
        Returns:
            URL de autorización
        """
        provider_name = provider or self.active_provider
        if not provider_name:
            raise ValueError("No hay proveedor activo")
        
        client = self.get_provider_client(provider_name)
        return client.get_authorization_url()
    
    def exchange_code_for_token(
        self,
        authorization_code: str,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Intercambiar código por tokens
        
        Args:
            authorization_code: Código de autorización
            provider: Nombre del proveedor (default: activo)
            
        Returns:
            Datos de tokens
        """
        provider_name = provider or self.active_provider
        if not provider_name:
            raise ValueError("No hay proveedor activo")
        
        client = self.get_provider_client(provider_name)
        return client.exchange_code_for_token(authorization_code)
    
    def get_valid_access_token(self, provider: Optional[str] = None) -> str:
        """
        Obtener access token válido
        
        Args:
            provider: Nombre del proveedor (default: activo)
            
        Returns:
            Access token válido
        """
        provider_name = provider or self.active_provider
        if not provider_name:
            raise ValueError("No hay proveedor activo")
        
        client = self.get_provider_client(provider_name)
        
        # Verificar y rotar token si es necesario
        rotation_manager = self.rotation_managers[provider_name]
        rotation_manager.check_and_rotate_token()
        
        return client.get_valid_access_token()
    
    def refresh_token(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Refrescar access token
        
        Args:
            provider: Nombre del proveedor (default: activo)
            
        Returns:
            Nuevos tokens
        """
        provider_name = provider or self.active_provider
        if not provider_name:
            raise ValueError("No hay proveedor activo")
        
        client = self.get_provider_client(provider_name)
        return client.refresh_access_token()
    
    def logout(self, provider: Optional[str] = None) -> bool:
        """
        Cerrar sesión
        
        Args:
            provider: Nombre del proveedor (default: activo)
            
        Returns:
            True si logout exitoso
        """
        provider_name = provider or self.active_provider
        if not provider_name:
            raise ValueError("No hay proveedor activo")
        
        client = self.get_provider_client(provider_name)
        return client.logout()
    
    def get_token_info(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener información de tokens
        
        Args:
            provider: Nombre del proveedor (default: activo)
            
        Returns:
            Información de tokens
        """
        provider_name = provider or self.active_provider
        if not provider_name:
            raise ValueError("No hay proveedor activo")
        
        client = self.get_provider_client(provider_name)
        return client.get_token_info()
    
    def get_rotation_history(
        self,
        provider: Optional[str] = None,
        limit: int = 10
    ) -> list:
        """
        Obtener historial de rotación de tokens
        
        Args:
            provider: Nombre del proveedor (default: activo)
            limit: Número máximo de entradas
            
        Returns:
            Historial de rotaciones
        """
        provider_name = provider or self.active_provider
        if not provider_name:
            raise ValueError("No hay proveedor activo")
        
        rotation_manager = self.rotation_managers[provider_name]
        return rotation_manager.get_rotation_history(limit)
    
    def check_all_tokens(self) -> Dict[str, bool]:
        """
        Verificar y rotar tokens de todos los proveedores
        
        Returns:
            Diccionario con estado de cada proveedor
        """
        results = {}
        
        for provider_name, rotation_manager in self.rotation_managers.items():
            results[provider_name] = rotation_manager.check_and_rotate_token()
        
        return results
