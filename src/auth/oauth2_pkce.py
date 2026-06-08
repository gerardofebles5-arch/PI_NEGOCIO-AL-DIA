"""
OAuth2 con PKCE y Token Rotation para (π)NAD V6.0
Implementación completa de OAuth2 con PKCE (Proof Key for Code Exchange)
y rotación automática de tokens para seguridad mejorada
"""

import secrets
import hashlib
import base64
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)


class OAuth2PKCEClient:
    """
    Cliente OAuth2 con PKCE para autenticación segura
    Implementa RFC 7636 (PKCE) y RFC 6749 (OAuth2)
    """
    
    def __init__(
        self,
        client_id: str,
        authorization_endpoint: str,
        token_endpoint: str,
        redirect_uri: str,
        scope: str = "openid profile email",
        token_rotation_enabled: bool = True,
        token_expiry_buffer: int = 300,  # 5 minutes buffer
    ):
        """
        Inicializar cliente OAuth2 PKCE
        
        Args:
            client_id: ID del cliente OAuth2
            authorization_endpoint: URL de autorización
            token_endpoint: URL de token
            redirect_uri: URI de redirección
            scope: Scopes solicitados
            token_rotation_enabled: Habilitar rotación de tokens
            token_expiry_buffer: Buffer en segundos antes de expiración
        """
        self.client_id = client_id
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.token_rotation_enabled = token_rotation_enabled
        self.token_expiry_buffer = token_expiry_buffer
        
        # Estado del cliente
        self.code_verifier: Optional[str] = None
        self.code_challenge: Optional[str] = None
        self.state: Optional[str] = None
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_type: Optional[str] = None
        self.expires_at: Optional[datetime] = None
        
        logger.info("OAuth2 PKCE Client inicializado")
    
    def generate_code_verifier(self, length: int = 128) -> str:
        """
        Generar code verifier aleatorio (RFC 7636)
        
        Args:
            length: Longitud del verifier en bytes
            
        Returns:
            Code verifier en base64url
        """
        self.code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(length)
        ).rstrip(b'=').decode('utf-8')
        logger.debug(f"Code verifier generado: {self.code_verifier[:10]}...")
        return self.code_verifier
    
    def generate_code_challenge(self) -> str:
        """
        Generar code challenge usando SHA-256 (RFC 7636)
        
        Returns:
            Code challenge en base64url
        """
        if self.code_verifier is None:
            self.generate_code_verifier()
        
        digest = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
        self.code_challenge = base64.urlsafe_b64encode(digest).rstrip(b'=').decode('utf-8')
        logger.debug(f"Code challenge generado: {self.code_challenge[:10]}...")
        return self.code_challenge
    
    def generate_state(self) -> str:
        """
        Generar state aleatorio para prevención CSRF
        
        Returns:
            State aleatorio en base64url
        """
        self.state = base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).rstrip(b'=').decode('utf-8')
        logger.debug(f"State generado: {self.state[:10]}...")
        return self.state
    
    def get_authorization_url(self) -> str:
        """
        Generar URL de autorización con PKCE
        
        Returns:
            URL de autorización completa
        """
        self.generate_code_challenge()
        self.generate_state()
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'code_challenge': self.code_challenge,
            'code_challenge_method': 'S256',
            'state': self.state,
        }
        
        auth_url = f"{self.authorization_endpoint}?{self._encode_params(params)}"
        logger.info(f"URL de autorización generada: {auth_url[:50]}...")
        return auth_url
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Intercambiar código de autorización por tokens
        
        Args:
            authorization_code: Código de autorización recibido
            
        Returns:
            Diccionario con tokens y metadata
        """
        if self.code_verifier is None:
            raise ValueError("Code verifier no generado. Llamar get_authorization_url primero.")
        
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'code_verifier': self.code_verifier,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            response = requests.post(
                self.token_endpoint,
                data=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            self._store_tokens(token_data)
            
            logger.info("Tokens intercambiados exitosamente")
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"Error intercambiando código por token: {e}")
            raise
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refrescar access token usando refresh token
        
        Returns:
            Diccionario con nuevos tokens
        """
        if self.refresh_token is None:
            raise ValueError("Refresh token no disponible")
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            response = requests.post(
                self.token_endpoint,
                data=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            self._store_tokens(token_data)
            
            logger.info("Access token refrescado exitosamente")
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"Error refrescando token: {e}")
            raise
    
    def is_token_expired(self) -> bool:
        """
        Verificar si el access token está expirado o cerca de expirar
        
        Returns:
            True si el token está expirado o cerca de expirar
        """
        if self.expires_at is None:
            return True
        
        expiry_threshold = datetime.now() + timedelta(seconds=self.token_expiry_buffer)
        return datetime.now() >= expiry_threshold
    
    def get_valid_access_token(self) -> str:
        """
        Obtener access token válido, refrescando si es necesario
        
        Returns:
            Access token válido
        """
        if self.access_token is None:
            raise ValueError("No access token disponible. Iniciar autenticación primero.")
        
        if self.token_rotation_enabled and self.is_token_expired():
            if self.refresh_token is not None:
                self.refresh_access_token()
            else:
                raise ValueError("Token expirado y no hay refresh token disponible")
        
        return self.access_token
    
    def revoke_token(self, token: Optional[str] = None) -> bool:
        """
        Revocar token (access o refresh)
        
        Args:
            token: Token a revocar (default: access token actual)
            
        Returns:
            True si el token fue revocado exitosamente
        """
        token_to_revoke = token or self.access_token
        
        if token_to_revoke is None:
            return False
        
        # Implementación depende del proveedor OAuth2
        # Ejemplo para Google OAuth2
        revoke_endpoint = "https://oauth2.googleapis.com/revoke"
        
        try:
            response = requests.post(
                revoke_endpoint,
                data={'token': token_to_revoke},
                timeout=30
            )
            response.raise_for_status()
            
            logger.info("Token revocado exitosamente")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Error revocando token: {e}")
            return False
    
    def logout(self) -> bool:
        """
        Cerrar sesión revocando tokens y limpiando estado
        
        Returns:
            True si el logout fue exitoso
        """
        success = True
        
        # Revocar access token
        if self.access_token:
            success = success and self.revoke_token(self.access_token)
        
        # Revocar refresh token
        if self.refresh_token:
            success = success and self.revoke_token(self.refresh_token)
        
        # Limpiar estado
        self.access_token = None
        self.refresh_token = None
        self.token_type = None
        self.expires_at = None
        self.code_verifier = None
        self.code_challenge = None
        self.state = None
        
        logger.info("Logout completado")
        return success
    
    def _store_tokens(self, token_data: Dict[str, Any]) -> None:
        """
        Almacenar tokens del response
        
        Args:
            token_data: Datos de tokens del response
        """
        self.access_token = token_data.get('access_token')
        self.refresh_token = token_data.get('refresh_token')
        self.token_type = token_data.get('token_type', 'Bearer')
        
        expires_in = token_data.get('expires_in')
        if expires_in:
            self.expires_at = datetime.now() + timedelta(seconds=int(expires_in))
        
        logger.debug("Tokens almacenados exitosamente")
    
    def _encode_params(self, params: Dict[str, Any]) -> str:
        """
        Codificar parámetros para URL
        
        Args:
            params: Diccionario de parámetros
            
        Returns:
            Parámetros codificados
        """
        return '&'.join(f"{k}={v}" for k, v in params.items())
    
    def get_token_info(self) -> Dict[str, Any]:
        """
        Obtener información sobre los tokens actuales
        
        Returns:
            Diccionario con información de tokens
        """
        return {
            'access_token': self.access_token[:20] + '...' if self.access_token else None,
            'refresh_token': self.refresh_token[:20] + '...' if self.refresh_token else None,
            'token_type': self.token_type,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_token_expired(),
            'token_rotation_enabled': self.token_rotation_enabled,
        }


class OAuth2TokenRotationManager:
    """
    Gestor de rotación automática de tokens OAuth2
    """
    
    def __init__(self, oauth_client: OAuth2PKCEClient):
        """
        Inicializar gestor de rotación
        
        Args:
            oauth_client: Cliente OAuth2 PKCE
        """
        self.oauth_client = oauth_client
        self.rotation_history: list = []
        
        logger.info("OAuth2 Token Rotation Manager inicializado")
    
    def check_and_rotate_token(self) -> bool:
        """
        Verificar y rotar token si es necesario
        
        Returns:
            True si el token fue rotado
        """
        if not self.oauth_client.token_rotation_enabled:
            return False
        
        if self.oauth_client.is_token_expired():
            try:
                old_token = self.oauth_client.access_token
                self.oauth_client.refresh_access_token()
                
                # Registrar rotación
                self.rotation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'old_token': old_token[:20] + '...' if old_token else None,
                    'new_token': self.oauth_client.access_token[:20] + '...',
                })
                
                logger.info("Token rotado exitosamente")
                return True
                
            except Exception as e:
                logger.error(f"Error rotando token: {e}")
                return False
        
        return False
    
    def get_rotation_history(self, limit: int = 10) -> list:
        """
        Obtener historial de rotaciones
        
        Args:
            limit: Número máximo de entradas
            
        Returns:
            Lista de rotaciones recientes
        """
        return self.rotation_history[-limit:]
