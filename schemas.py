from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime
from security.validations import CPF, CNPJ, Telefone

# Empresa
class EmpresaSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    cnpj: CNPJ 
    telefone: Telefone

class EmpresaResponse(BaseModel):
    id: int
    nome: str 
    email: EmailStr
    cnpj: str
    created_at: datetime

    class Config:
        from_attributes = True

class EmpresaUpdate(BaseModel):
    nome: Optional[str] = None
    email : Optional[EmailStr] = None
    senha : Optional[str] = None
    telefone : Optional[Telefone] = None

# Usuarios
class UsuarioSchema(BaseModel):
    nome: str
    sobrenome: str
    email: EmailStr
    senha: str
    cpf: CPF
    telefone: Telefone

class UsuarioResponse(BaseModel):
    id: int
    nome: str 
    sobrenome: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class UsuarioVincularToken(BaseModel):
    invite_key: str 

class UsuarioUpdate(BaseModel):
    email : Optional[EmailStr] = None
    senha : Optional[str] = None
    telefone : Optional[Telefone] = None

# Token
class TokenResponse(BaseModel):
    key: str 
    expira_em: datetime
    usado: bool

# Cliente
class ClienteSchema(BaseModel):
    nome: str 
    email: EmailStr
    cpf: CPF 
    telefone: Telefone
    descricao_servico: Optional[str] = None

class ClienteResponse(BaseModel):
    id: int 
    nome: str 
    descricao_servico: Optional[str] = None

class ClienteUpdateStatus(BaseModel):
    prioridade: Literal['novo_contato', 'em_atendimento', 'proposta_enviada', 'negociacao', 'fechado']
    valor: Optional[float] = None

class ClienteInfoUpdate(BaseModel):
    nome: Optional[str] = None 
    email: Optional[EmailStr] = None 
    telefone: Optional[str] = None
    descricao_servico: Optional[str] = None 

class ResponsavelClienteUpdate(BaseModel):
    usuario_id: Optional[int] = None
