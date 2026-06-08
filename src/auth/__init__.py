"""
Paquete de autenticación para (π)NAD
"""

from .gmail_oauth import GmailOAuth, OAuthCredentialsManager, TokenManager
from .jwt_auth import JWTAuth, TokenManager as JWTTokenManager, require_auth, require_role, PermissionManager

__all__ = ['GmailOAuth', 'OAuthCredentialsManager', 'TokenManager', 'JWTAuth', 'JWTTokenManager', 'require_auth', 'require_role', 'PermissionManager']
