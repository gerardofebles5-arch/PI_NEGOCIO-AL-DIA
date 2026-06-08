"""
Sistema de autenticación JWT para (π)NAD
"""

import jwt
import datetime
from typing import Dict, Optional
from functools import wraps
from flask import request, jsonify
from src.utils.logger import get_logger
from src.utils.exceptions import AuthenticationException


class JWTAuth:
    """Gestor de autenticación JWT para (π)NAD"""
    
    def __init__(self, secret_key: str = None, algorithm: str = 'HS256', 
                 token_expiration: int = 3600):
        """
        Inicializar gestor JWT
        
        Args:
            secret_key: Clave secreta para firmar tokens
            algorithm: Algoritmo de firma
            token_expiration: Tiempo de expiración del token en segundos
        """
        self.secret_key = secret_key or 'default_jwt_secret_key_change_in_production'
        self.algorithm = algorithm
        self.token_expiration = token_expiration
        self.logger = get_logger('jwt_auth')
    
    def generate_token(self, user_id: str, user_type: str = 'client', 
                     additional_claims: Dict = None) -> str:
        """
        Generar token JWT
        
        Args:
            user_id: ID del usuario
            user_type: Tipo de usuario (client, validator, admin)
            additional_claims: Claims adicionales
            
        Returns:
            Token JWT
        """
        try:
            payload = {
                'user_id': user_id,
                'user_type': user_type,
                'iat': datetime.datetime.utcnow(),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.token_expiration)
            }
            
            if additional_claims:
                payload.update(additional_claims)
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            
            self.logger.info(f"Token generado para usuario {user_id}")
            
            return token
        except Exception as e:
            self.logger.error(f"Error generando token: {e}")
            raise AuthenticationException(f"Error generando token: {e}", user_id=user_id)
    
    def decode_token(self, token: str) -> Dict:
        """
        Decodificar token JWT
        
        Args:
            token: Token JWT
            
        Returns:
            Payload del token
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            self.logger.info(f"Token decodificado para usuario {payload.get('user_id')}")
            
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expirado")
            raise AuthenticationException("Token expirado")
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Token inválido: {e}")
            raise AuthenticationException("Token inválido")
    
    def verify_token(self, token: str) -> bool:
        """
        Verificar token JWT
        
        Args:
            token: Token JWT
            
        Returns:
            True si válido, False si no
        """
        try:
            self.decode_token(token)
            return True
        except AuthenticationException:
            return False
    
    def refresh_token(self, token: str) -> str:
        """
        Refrescar token JWT
        
        Args:
            token: Token JWT a refrescar
            
        Returns:
            Nuevo token JWT
        """
        try:
            payload = self.decode_token(token)
            
            # Generar nuevo token con los mismos claims
            new_token = self.generate_token(
                user_id=payload['user_id'],
                user_type=payload['user_type'],
                additional_claims={k: v for k, v in payload.items() 
                                 if k not in ['iat', 'exp']}
            )
            
            self.logger.info(f"Token refrescado para usuario {payload['user_id']}")
            
            return new_token
        except AuthenticationException as e:
            self.logger.error(f"Error refrescando token: {e}")
            raise AuthenticationException(f"Error refrescando token: {e}")
    
    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Obtener ID de usuario desde token
        
        Args:
            token: Token JWT
            
        Returns:
            ID de usuario o None
        """
        try:
            payload = self.decode_token(token)
            return payload.get('user_id')
        except AuthenticationException:
            return None
    
    def get_user_type_from_token(self, token: str) -> Optional[str]:
        """
        Obtener tipo de usuario desde token
        
        Args:
            token: Token JWT
            
        Returns:
            Tipo de usuario o None
        """
        try:
            payload = self.decode_token(token)
            return payload.get('user_type')
        except AuthenticationException:
            return None


class TokenManager:
    """Gestor de tokens para (π)NAD"""
    
    def __init__(self, jwt_auth: JWTAuth = None):
        """
        Inicializar gestor de tokens
        
        Args:
            jwt_auth: Instancia de JWTAuth
        """
        self.jwt_auth = jwt_auth or JWTAuth()
        self.logger = get_logger('token_manager')
    
    def create_access_token(self, user_id: str, user_type: str = 'client') -> Dict:
        """
        Crear token de acceso
        
        Args:
            user_id: ID del usuario
            user_type: Tipo de usuario
            
        Returns:
            Diccionario con token y metadata
        """
        token = self.jwt_auth.generate_token(user_id, user_type)
        
        return {
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': self.jwt_auth.token_expiration,
            'user_id': user_id,
            'user_type': user_type
        }
    
    def create_refresh_token(self, user_id: str, user_type: str = 'client') -> str:
        """
        Crear token de refresco (con expiración más larga)
        
        Args:
            user_id: ID del usuario
            user_type: Tipo de usuario
            
        Returns:
            Token de refresco
        """
        # Token de refresco con expiración de 7 días
        old_expiration = self.jwt_auth.token_expiration
        self.jwt_auth.token_expiration = 7 * 24 * 3600  # 7 días
        
        token = self.jwt_auth.generate_token(
            user_id, 
            user_type,
            additional_claims={'token_type': 'refresh'}
        )
        
        self.jwt_auth.token_expiration = old_expiration
        
        return token
    
    def verify_access_token(self, token: str) -> Dict:
        """
        Verificar token de acceso
        
        Args:
            token: Token de acceso
            
        Returns:
            Payload del token
        """
        return self.jwt_auth.decode_token(token)
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refrescar token de acceso usando token de refresco
        
        Args:
            refresh_token: Token de refresco
            
        Returns:
            Nuevo token de acceso
        """
        payload = self.jwt_auth.decode_token(refresh_token)
        
        if payload.get('token_type') != 'refresh':
            raise AuthenticationException("Token de refresco inválido")
        
        new_access_token = self.jwt_auth.generate_token(
            payload['user_id'],
            payload['user_type']
        )
        
        return {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': self.jwt_auth.token_expiration
        }


def require_auth(jwt_auth: JWTAuth = None):
    """
    Decorador para requerir autenticación JWT
    
    Args:
        jwt_auth: Instancia de JWTAuth
        
    Returns:
        Decorador
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth = jwt_auth or JWTAuth()
            token = None
            
            # Obtener token del header Authorization
            auth_header = request.headers.get('Authorization')
            
            if auth_header:
                try:
                    token = auth_header.split(' ')[1]  # Bearer <token>
                except IndexError:
                    return jsonify({'error': 'Formato de token inválido'}), 401
            
            if not token:
                return jsonify({'error': 'Token no proporcionado'}), 401
            
            try:
                payload = auth.decode_token(token)
                request.current_user = payload
                return f(*args, **kwargs)
            except AuthenticationException as e:
                return jsonify({'error': str(e)}), 401
        
        return decorated_function
    return decorator


def require_role(required_role: str, jwt_auth: JWTAuth = None):
    """
    Decorador para requerir rol específico
    
    Args:
        required_role: Rol requerido (client, validator, admin)
        jwt_auth: Instancia de JWTAuth
        
    Returns:
        Decorador
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth = jwt_auth or JWTAuth()
            token = None
            
            auth_header = request.headers.get('Authorization')
            
            if auth_header:
                try:
                    token = auth_header.split(' ')[1]
                except IndexError:
                    return jsonify({'error': 'Formato de token inválido'}), 401
            
            if not token:
                return jsonify({'error': 'Token no proporcionado'}), 401
            
            try:
                payload = auth.decode_token(token)
                user_type = payload.get('user_type')
                
                if user_type != required_role and user_type != 'admin':
                    return jsonify({'error': 'Permisos insuficientes'}), 403
                
                request.current_user = payload
                return f(*args, **kwargs)
            except AuthenticationException as e:
                return jsonify({'error': str(e)}), 401
        
        return decorated_function
    return decorator


class PermissionManager:
    """Gestor de permisos para (π)NAD"""
    
    PERMISSIONS = {
        'client': [
            'view_own_dashboard',
            'upload_own_documents',
            'view_own_documents',
            'view_own_transactions',
            'request_validation'
        ],
        'validator': [
            'view_assigned_clients',
            'validate_transactions',
            'view_client_documents',
            'add_validation_notes'
        ],
        'admin': [
            'view_all_clients',
            'manage_clients',
            'manage_validators',
            'view_all_transactions',
            'manage_system',
            'view_analytics'
        ]
    }
    
    @classmethod
    def has_permission(cls, user_type: str, permission: str) -> bool:
        """
        Verificar si usuario tiene permiso
        
        Args:
            user_type: Tipo de usuario
            permission: Permiso a verificar
            
        Returns:
            True si tiene permiso
        """
        if user_type == 'admin':
            return True  # Admin tiene todos los permisos
        
        return permission in cls.PERMISSIONS.get(user_type, [])
    
    @classmethod
    def get_permissions(cls, user_type: str) -> list:
        """
        Obtener permisos de usuario
        
        Args:
            user_type: Tipo de usuario
            
        Returns:
            Lista de permisos
        """
        return cls.PERMISSIONS.get(user_type, [])
