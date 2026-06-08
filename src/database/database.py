"""
Configuración de base de datos con SQLAlchemy para (π)NAD
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import os
from src.utils.logger import get_logger
from src.database.models import Base


class DatabaseManager:
    """Gestor de base de datos para (π)NAD"""
    
    def __init__(self, database_url: str = None, echo: bool = False):
        """
        Inicializar gestor de base de datos
        
        Args:
            database_url: URL de conexión a la base de datos
            echo: Mostrar queries SQL (para debug)
        """
        self.database_url = database_url or os.getenv(
            'DATABASE_URL',
            'postgresql://pinad_user:pinad_password@localhost:5432/pinad_db'
        )
        self.echo = echo
        self.logger = get_logger('database')
        
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Inicializar motor de base de datos"""
        try:
            self.engine = create_engine(
                self.database_url,
                echo=self.echo,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.logger.info("Base de datos inicializada exitosamente")
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    def create_tables(self):
        """Crear todas las tablas"""
        try:
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("Tablas creadas exitosamente")
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
            raise
    
    def drop_tables(self):
        """Eliminar todas las tablas"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            self.logger.info("Tablas eliminadas exitosamente")
        except Exception as e:
            self.logger.error(f"Error eliminando tablas: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Obtener sesión de base de datos
        
        Yields:
            Sesión de SQLAlchemy
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error en sesión de base de datos: {e}")
            raise
        finally:
            session.close()
    
    def get_engine(self):
        """Obtener motor de base de datos"""
        return self.engine
    
    def dispose(self):
        """Cerrar conexión a base de datos"""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Conexión a base de datos cerrada")


class Repository:
    """Repositorio base para operaciones de base de datos"""
    
    def __init__(self, session: Session):
        """
        Inicializar repositorio
        
        Args:
            session: Sesión de SQLAlchemy
        """
        self.session = session
    
    def add(self, model):
        """
        Añadir modelo a sesión
        
        Args:
            model: Modelo a añadir
        """
        self.session.add(model)
    
    def update(self, model):
        """
        Actualizar modelo en sesión
        
        Args:
            model: Modelo a actualizar
        """
        self.session.add(model)
    
    def delete(self, model):
        """
        Eliminar modelo de sesión
        
        Args:
            model: Modelo a eliminar
        """
        self.session.delete(model)
    
    def commit(self):
        """Commit de sesión"""
        self.session.commit()
    
    def rollback(self):
        """Rollback de sesión"""
        self.session.rollback()
    
    def refresh(self, model):
        """
        Refrescar modelo desde base de datos
        
        Args:
            model: Modelo a refrescar
        """
        self.session.refresh(model)
    
    def expire(self, model):
        """
        Expirar modelo de sesión
        
        Args:
            model: Modelo a expirar
        """
        self.session.expire(model)


class ClientRepository(Repository):
    """Repositorio de clientes"""
    
    def get_by_id(self, client_id: str):
        """Obtener cliente por ID"""
        from src.database.models import Client
        return self.session.query(Client).filter(Client.client_id == client_id).first()
    
    def get_by_rif(self, rif: str):
        """Obtener cliente por RIF"""
        from src.database.models import Client
        return self.session.query(Client).filter(Client.rif == rif).first()
    
    def get_by_email(self, email: str):
        """Obtener cliente por email"""
        from src.database.models import Client
        return self.session.query(Client).filter(Client.email == email).first()
    
    def get_all(self, skip: int = 0, limit: int = 100):
        """Obtener todos los clientes"""
        from src.database.models import Client
        return self.session.query(Client).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100):
        """Obtener clientes por estado"""
        from src.database.models import Client
        return self.session.query(Client).filter(Client.status == status).offset(skip).limit(limit).all()
    
    def get_by_plan(self, plan: str, skip: int = 0, limit: int = 100):
        """Obtener clientes por plan"""
        from src.database.models import Client
        return self.session.query(Client).filter(Client.plan == plan).offset(skip).limit(limit).all()


class TransactionRepository(Repository):
    """Repositorio de transacciones"""
    
    def get_by_id(self, transaction_id: str):
        """Obtener transacción por ID"""
        from src.database.models import Transaction
        return self.session.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    
    def get_by_client_id(self, client_id: str, skip: int = 0, limit: int = 100):
        """Obtener transacciones de cliente"""
        from src.database.models import Transaction
        return self.session.query(Transaction).filter(Transaction.client_id == client_id).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100):
        """Obtener transacciones por estado"""
        from src.database.models import Transaction
        return self.session.query(Transaction).filter(Transaction.status == status).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, start_date, end_date, client_id: str = None):
        """Obtener transacciones por rango de fechas"""
        from src.database.models import Transaction
        query = self.session.query(Transaction).filter(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        )
        if client_id:
            query = query.filter(Transaction.client_id == client_id)
        return query.all()
    
    def get_summary(self, client_id: str, start_date, end_date):
        """Obtener resumen de transacciones"""
        from src.database.models import Transaction
        from sqlalchemy import func
        
        result = self.session.query(
            func.sum(Transaction.amount).label('total'),
            func.count(Transaction.transaction_id).label('count')
        ).filter(
            Transaction.client_id == client_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).first()
        
        return {
            'total': result.total or 0,
            'count': result.count or 0
        }


class DocumentRepository(Repository):
    """Repositorio de documentos"""
    
    def get_by_id(self, document_id: str):
        """Obtener documento por ID"""
        from src.database.models import Document
        return self.session.query(Document).filter(Document.document_id == document_id).first()
    
    def get_by_client_id(self, client_id: str, skip: int = 0, limit: int = 100):
        """Obtener documentos de cliente"""
        from src.database.models import Document
        return self.session.query(Document).filter(Document.client_id == client_id).offset(skip).limit(limit).all()
    
    def get_by_type(self, document_type: str, skip: int = 0, limit: int = 100):
        """Obtener documentos por tipo"""
        from src.database.models import Document
        return self.session.query(Document).filter(Document.document_type == document_type).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100):
        """Obtener documentos por estado"""
        from src.database.models import Document
        return self.session.query(Document).filter(Document.processing_status == status).offset(skip).limit(limit).all()


class ValidationRepository(Repository):
    """Repositorio de validaciones"""
    
    def get_by_id(self, validation_id: str):
        """Obtener validación por ID"""
        from src.database.models import Validation
        return self.session.query(Validation).filter(Validation.validation_id == validation_id).first()
    
    def get_by_client_id(self, client_id: str, skip: int = 0, limit: int = 100):
        """Obtener validaciones de cliente"""
        from src.database.models import Validation
        return self.session.query(Validation).filter(Validation.client_id == client_id).offset(skip).limit(limit).all()
    
    def get_by_validator_id(self, validator_id: str, skip: int = 0, limit: int = 100):
        """Obtener validaciones de asesor"""
        from src.database.models import Validation
        return self.session.query(Validation).filter(Validation.validator_id == validator_id).offset(skip).limit(limit).all()
    
    def get_pending_by_validator(self, validator_id: str):
        """Obtener validaciones pendientes de asesor"""
        from src.database.models import Validation
        return self.session.query(Validation).filter(
            Validation.validator_id == validator_id
        ).all()


class ValidatorRepository(Repository):
    """Repositorio de asesores"""
    
    def get_by_id(self, validator_id: str):
        """Obtener asesor por ID"""
        from src.database.models import Validator
        return self.session.query(Validator).filter(Validator.validator_id == validator_id).first()
    
    def get_by_email(self, email: str):
        """Obtener asesor por email"""
        from src.database.models import Validator
        return self.session.query(Validator).filter(Validator.email == email).first()
    
    def get_all(self, skip: int = 0, limit: int = 100):
        """Obtener todos los asesores"""
        from src.database.models import Validator
        return self.session.query(Validator).offset(skip).limit(limit).all()
    
    def get_available(self, skip: int = 0, limit: int = 100):
        """Obtener asesores disponibles (con capacidad)"""
        from src.database.models import Validator, Client
        return self.session.query(Validator).outerjoin(
            Client, Validator.validator_id == Client.assigned_advisor_id
        ).group_by(Validator.validator_id).having(
            func.count(Client.client_id) < Validator.max_clients
        ).offset(skip).limit(limit).all()
