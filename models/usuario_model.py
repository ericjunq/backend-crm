from sqlalchemy import Column, Integer, Boolean, DateTime, String, func, ForeignKey
from database import Base
from sqlalchemy.orm import relationship
from enums import CargosEnum
from sqlalchemy import Enum as SAEnum


class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(25), nullable=False)
    sobrenome = Column(String(40), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    cpf = Column(String, nullable=False, unique=True)
    telefone = Column(String, nullable=False, unique=True)
    cargo = Column(SAEnum(CargosEnum), default=CargosEnum.funcionario, nullable=False)
    ativo = Column(Boolean, default=True)
    status_empresa = Column(Boolean, default=None, nullable=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    empresa = relationship('Empresa', back_populates='usuarios')
    clientes = relationship('Cliente', back_populates='responsavel')
    interacoes = relationship('Interacao', back_populates='usuario')



