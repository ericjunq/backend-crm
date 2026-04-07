from sqlalchemy import Column, Integer, Boolean, DateTime, String, func, ForeignKey
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SAEnum
from enums import TiposInteracoesEnum

class Interacao(Base):
    __tablename__ = 'interacoes'

    id=Column(Integer, autoincrement=True, primary_key=True)
    tipo = Column(SAEnum(TiposInteracoesEnum), nullable=False)
    descricao = Column(String(80), nullable=False)

    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)

    cliente = relationship('Cliente', back_populates='interacoes')
    usuario_id = relationship('Usuario', back_populates='interacoes')