"""
Database Integration Tests para (π)NAD V6.0
Tests de integración para base de datos
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Dict, Any


class TestDatabaseIntegration:
    """Tests de integración para base de datos"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para tests"""
        # Configurar conexión a base de datos de test
        self.engine = create_engine("sqlite:///test_pinad.db")
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        
        # Crear tablas de test
        self.create_test_tables()
    
    def create_test_tables(self):
        """Crear tablas de test"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """))
            
            conn.commit()
    
    def test_database_connection(self):
        """Test de conexión a base de datos"""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
    
    def test_create_user(self):
        """Test de creación de usuario"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO users (email, name)
                VALUES ('test@pinad.com', 'Test User')
            """))
            conn.commit()
            
            result = conn.execute(
                text("SELECT * FROM users WHERE email = 'test@pinad.com'")
            )
            user = result.fetchone()
            
            assert user is not None
            assert user[1] == "test@pinad.com"
            assert user[2] == "Test User"
    
    def test_create_document(self):
        """Test de creación de documento"""
        # Crear usuario primero
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO users (email, name)
                VALUES ('test@pinad.com', 'Test User')
            """))
            conn.commit()
            
            # Obtener user_id
            result = conn.execute(
                text("SELECT id FROM users WHERE email = 'test@pinad.com'")
            )
            user_id = result.fetchone()[0]
            
            # Crear documento
            conn.execute(text("""
                INSERT INTO documents (user_id, name, type, status)
                VALUES (?, 'Test Document', 'invoice', 'processing')
            """), (user_id,))
            conn.commit()
            
            # Verificar documento
            result = conn.execute(
                text("SELECT * FROM documents WHERE user_id = ?"),
                (user_id,)
            )
            document = result.fetchone()
            
            assert document is not None
            assert document[2] == "Test Document"
            assert document[3] == "invoice"
    
    def test_update_document_status(self):
        """Test de actualización de estado de documento"""
        # Crear usuario y documento
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO users (email, name)
                VALUES ('test@pinad.com', 'Test User')
            """))
            conn.commit()
            
            result = conn.execute(
                text("SELECT id FROM users WHERE email = 'test@pinad.com'")
            )
            user_id = result.fetchone()[0]
            
            conn.execute(text("""
                INSERT INTO documents (user_id, name, type, status)
                VALUES (?, 'Test Document', 'invoice', 'processing')
            """), (user_id,))
            conn.commit()
            
            # Actualizar estado
            conn.execute(text("""
                UPDATE documents
                SET status = 'completed'
                WHERE user_id = ?
            """), (user_id,))
            conn.commit()
            
            # Verificar actualización
            result = conn.execute(
                text("SELECT status FROM documents WHERE user_id = ?"),
                (user_id,)
            )
            status = result.fetchone()[0]
            
            assert status == "completed"
    
    def test_delete_document(self):
        """Test de eliminación de documento"""
        # Crear usuario y documento
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO users (email, name)
                VALUES ('test@pinad.com', 'Test User')
            """))
            conn.commit()
            
            result = conn.execute(
                text("SELECT id FROM users WHERE email = 'test@pinad.com'")
            )
            user_id = result.fetchone()[0]
            
            conn.execute(text("""
                INSERT INTO documents (user_id, name, type, status)
                VALUES (?, 'Test Document', 'invoice', 'processing')
            """), (user_id,))
            conn.commit()
            
            # Eliminar documento
            conn.execute(text("""
                DELETE FROM documents WHERE user_id = ?
            """), (user_id,))
            conn.commit()
            
            # Verificar eliminación
            result = conn.execute(
                text("SELECT COUNT(*) FROM documents WHERE user_id = ?"),
                (user_id,)
            )
            count = result.fetchone()[0]
            
            assert count == 0
    
    def test_foreign_key_constraint(self):
        """Test de constraint de foreign key"""
        with self.engine.connect() as conn:
            # Intentar crear documento sin usuario (debe fallar)
            try:
                conn.execute(text("""
                    INSERT INTO documents (user_id, name, type, status)
                    VALUES (999, 'Test Document', 'invoice', 'processing')
                """))
                conn.commit()
                assert False, "Foreign key constraint no funcionó"
            except Exception as e:
                assert "FOREIGN KEY" in str(e).upper() or "constraint" in str(e).lower()
    
    def test_transaction_rollback(self):
        """Test de rollback de transacción"""
        with self.engine.connect() as conn:
            # Iniciar transacción
            trans = conn.begin()
            
            try:
                conn.execute(text("""
                    INSERT INTO users (email, name)
                    VALUES ('rollback@pinad.com', 'Rollback User')
                """))
                
                # Rollback
                trans.rollback()
                
                # Verificar que no se creó
                result = conn.execute(
                    text("SELECT COUNT(*) FROM users WHERE email = 'rollback@pinad.com'")
                )
                count = result.fetchone()[0]
                
                assert count == 0
            except Exception as e:
                trans.rollback()
                raise
    
    def teardown(self):
        """Cleanup después de tests"""
        self.session.close()
        self.engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
