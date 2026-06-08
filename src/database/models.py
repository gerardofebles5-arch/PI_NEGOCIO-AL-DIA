"""
Modelos de base de datos con SQLAlchemy para (π)NAD
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


Base = declarative_base()


class ClientStatus(enum.Enum):
    """Estado del cliente"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class ClientPlan(enum.Enum):
    """Plan del cliente"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class TransactionType(enum.Enum):
    """Tipo de transacción"""
    SALE = "sale"
    PURCHASE = "purchase"
    EXPENSE = "expense"


class TransactionStatus(enum.Enum):
    """Estado de transacción"""
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"
    OBSERVED = "observed"


class DocumentType(enum.Enum):
    """Tipo de documento"""
    REPORT_Z = "report_z"
    INVOICE_SALE = "invoice_sale"
    INVOICE_PURCHASE = "invoice_purchase"
    DATABASE = "database"


class DocumentStatus(enum.Enum):
    """Estado de documento"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class ValidationAction(enum.Enum):
    """Acción de validación"""
    APPROVE = "approve"
    REJECT = "reject"
    OBSERVE = "observe"


class Client(Base):
    """Modelo de Cliente"""
    __tablename__ = 'clients'
    
    client_id = Column(String(36), primary_key=True)
    rif = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    sector = Column(String(50))
    plan = Column(SQLEnum(ClientPlan), default=ClientPlan.BASIC)
    status = Column(SQLEnum(ClientStatus), default=ClientStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_advisor_id = Column(String(36), ForeignKey('validators.validator_id'))
    
    # Relaciones
    transactions = relationship("Transaction", back_populates="client", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="client", cascade="all, delete-orphan")
    validations = relationship("Validation", back_populates="client", cascade="all, delete-orphan")
    assigned_advisor = relationship("Validator", back_populates="assigned_clients")
    
    def __repr__(self):
        return f"<Client(client_id='{self.client_id}', rif='{self.rif}', name='{self.name}')>"


class Validator(Base):
    """Modelo de Asesor Contable"""
    __tablename__ = 'validators'
    
    validator_id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    specialization = Column(String(100))
    max_clients = Column(Integer, default=50)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    assigned_clients = relationship("Client", back_populates="assigned_advisor")
    validations = relationship("Validation", back_populates="validator", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Validator(validator_id='{self.validator_id}', name='{self.name}')>"


class Transaction(Base):
    """Modelo de Transacción"""
    __tablename__ = 'transactions'
    
    transaction_id = Column(String(36), primary_key=True)
    client_id = Column(String(36), ForeignKey('clients.client_id'), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey('documents.document_id'))
    transaction_date = Column(DateTime, nullable=False, index=True)
    type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float)
    tax_rate = Column(Float)
    description = Column(Text)
    category = Column(String(100))
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, index=True)
    validated_by = Column(String(36), ForeignKey('validators.validator_id'))
    validation_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    client = relationship("Client", back_populates="transactions")
    document = relationship("Document", back_populates="transactions")
    validator = relationship("Validator", backref="validated_transactions")
    
    def __repr__(self):
        return f"<Transaction(transaction_id='{self.transaction_id}', type='{self.type}', amount={self.amount})>"


class Document(Base):
    """Modelo de Documento"""
    __tablename__ = 'documents'
    
    document_id = Column(String(36), primary_key=True)
    client_id = Column(String(36), ForeignKey('clients.client_id'), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(10))
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING)
    ocr_confidence = Column(Float)
    extraction_date = Column(DateTime)
    raw_text = Column(Text)
    extracted_data = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    client = relationship("Client", back_populates="documents")
    transactions = relationship("Transaction", back_populates="document")
    
    def __repr__(self):
        return f"<Document(document_id='{self.document_id}', type='{self.document_type}', status='{self.processing_status}')>"


class Validation(Base):
    """Modelo de Validación"""
    __tablename__ = 'validations'
    
    validation_id = Column(String(36), primary_key=True)
    document_id = Column(String(36), ForeignKey('documents.document_id'), nullable=False)
    client_id = Column(String(36), ForeignKey('clients.client_id'), nullable=False, index=True)
    validator_id = Column(String(36), ForeignKey('validators.validator_id'), nullable=False)
    action = Column(SQLEnum(ValidationAction), nullable=False)
    notes = Column(Text)
    previous_status = Column(String(20))
    new_status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    client = relationship("Client", back_populates="validations")
    validator = relationship("Validator", back_populates="validations")
    
    def __repr__(self):
        return f"<Validation(validation_id='{self.validation_id}', action='{self.action}')>"


class DashboardData(Base):
    """Modelo de Datos de Dashboard"""
    __tablename__ = 'dashboard_data'
    
    data_id = Column(String(36), primary_key=True)
    client_id = Column(String(36), ForeignKey('clients.client_id'), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    revenue = Column(Float, default=0)
    expenses = Column(Float, default=0)
    net_income = Column(Float, default=0)
    tax_collected = Column(Float, default=0)
    tax_paid = Column(Float, default=0)
    transaction_count = Column(Integer, default=0)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    client = relationship("Client")
    
    def __repr__(self):
        return f"<DashboardData(data_id='{self.data_id}', date='{self.date}', revenue={self.revenue})>"


class Notification(Base):
    """Modelo de Notificación"""
    __tablename__ = 'notifications'
    
    notification_id = Column(String(36), primary_key=True)
    client_id = Column(String(36), ForeignKey('clients.client_id'), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), default='unread')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    read_at = Column(DateTime)
    
    # Relaciones
    client = relationship("Client")
    
    def __repr__(self):
        return f"<Notification(notification_id='{self.notification_id}', type='{self.type}', status='{self.status}')>"


class Webhook(Base):
    """Modelo de Webhook"""
    __tablename__ = 'webhooks'
    
    webhook_id = Column(String(36), primary_key=True)
    client_id = Column(String(36), ForeignKey('clients.client_id'), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    events = Column(Text)  # JSON string de eventos
    secret = Column(String(100))
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    client = relationship("Client")
    
    def __repr__(self):
        return f"<Webhook(webhook_id='{self.webhook_id}', url='{self.url}', status='{self.status}')>"


class AuditLog(Base):
    """Modelo de Log de Auditoría"""
    __tablename__ = 'audit_logs'
    
    log_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(36))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(Text)  # JSON string
    
    def __repr__(self):
        return f"<AuditLog(log_id='{self.log_id}', action='{self.action}', timestamp='{self.timestamp}')>"
