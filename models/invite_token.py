from sqlalchemy import Column, Boolean, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base
from security.security import gerar_token_invite

class TokenInvite(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, unique=True, nullable=False, default=gerar_token_invite)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=False)
    usado = Column(Boolean, default=False)
    expira_em = Column(DateTime, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    empresa = relationship('Empresa', back_populates='token_invites')