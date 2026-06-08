"""
Tests para el sistema de caché
"""

import pytest
from src.cache.redis_cache import RedisCache, CacheManager


class TestRedisCache:
    """Tests para RedisCache"""
    
    @pytest.fixture
    def cache(self):
        """Fixture para RedisCache"""
        return RedisCache()
    
    def test_initialization(self, cache):
        """Test de inicialización"""
        assert cache is not None
        assert cache.host == 'localhost'
        assert cache.port == 6379
    
    def test_set_get(self, cache):
        """Test de set y get"""
        if not cache.client:
            pytest.skip("Redis no disponible")
        
        cache.set('test_key', 'test_value')
        value = cache.get('test_key')
        assert value == 'test_value'
        cache.delete('test_key')
    
    def test_exists(self, cache):
        """Test de exists"""
        if not cache.client:
            pytest.skip("Redis no disponible")
        
        cache.set('test_key', 'test_value')
        assert cache.exists('test_key') is True
        cache.delete('test_key')
        assert cache.exists('test_key') is False
    
    def test_delete(self, cache):
        """Test de delete"""
        if not cache.client:
            pytest.skip("Redis no disponible")
        
        cache.set('test_key', 'test_value')
        assert cache.delete('test_key') is True
        assert cache.exists('test_key') is False


class TestCacheManager:
    """Tests para CacheManager"""
    
    @pytest.fixture
    def cache_manager(self):
        """Fixture para CacheManager"""
        return CacheManager()
    
    def test_initialization(self, cache_manager):
        """Test de inicialización"""
        assert cache_manager is not None
        assert cache_manager.cache is not None
    
    def test_cache_client_data(self, cache_manager):
        """Test de caché de datos de cliente"""
        if not cache_manager.cache.client:
            pytest.skip("Redis no disponible")
        
        client_data = {
            'client_id': 'test_client',
            'name': 'Test Client',
            'email': 'test@example.com'
        }
        
        cache_manager.cache_client_data('test_client', client_data)
        cached_data = cache_manager.get_client_data('test_client')
        assert cached_data is not None
        assert cached_data['name'] == 'Test Client'
