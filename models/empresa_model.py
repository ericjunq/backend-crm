from sqlalchemy import Column, Integer, Boolean, DateTime, String, func, ForeignKey
from database import Base
from sqlalchemy.orm import relationship
import uuid

class Empresa(Base):
    __tablename__ = 'empresas'

    id = Column(Integer, autoincrement=True, primary_key=True)
    nome = Column(String(40), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)
    cnpj = Column(String, nullable=False, unique=True)
    telefone = Column(String(17), nullable=False, unique=True)
    invite_key = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    usuarios = relationship('Usuario', back_populates='empresa')
    clientes = relationship('Cliente', back_populates='empresa')
    token_invite = relationship('TokenInvite', back_populates='empresa')