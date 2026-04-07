from enums import PrioridadeEnum
from sqlalchemy import Column, Float, Integer, DateTime, String, func, ForeignKey
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SAEnum

class Cliente(Base):
    __tablename__ = 'clientes'

    id = Column(Integer, autoincrement=True, primary_key=True)
    nome = Column(String(40), nullable=False)
    email = Column(String(50), nullable=False)
    telefone = Column(String(17), nullable=False)
    valor_venda = Column(Float)
    cpf = Column(String(14), unique=True, nullable=False)
    descricao_servico = Column(String(70), nullable=True)
    prioridade = Column(SAEnum(PrioridadeEnum), default=PrioridadeEnum.novo_contato, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    responsavel_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)

    empresa = relationship('Empresa', back_populates='clientes')
    responsavel = relationship('Usuario', back_populates='clientes')
    interacoes = relationship('Interacao', back_populates='cliente')