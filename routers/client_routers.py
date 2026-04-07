from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas import ResponsavelClienteUpdate, ClienteInfoUpdate, ClienteResponse, ClienteSchema, ClienteUpdateStatus
from models.cliente_model import Cliente
from security.security import get_current_empresa, get_current_usuario
from models.usuario_model import Usuario
from models.empresa_model import Empresa
from typing import Optional, List
from enums import PrioridadeEnum
from datetime import datetime

client_router = APIRouter(prefix='/cliente', tags=['cliente'])

# Func de cadastro
def cadastrar_cliente(
    clienteschema: ClienteSchema,
    empresa_id: int,
    db: Session
):
    cliente = Cliente(
        nome = clienteschema.nome,
        email = clienteschema.email,
        telefone = clienteschema.telefone,
        cpf = clienteschema.cpf,
        empresa_id = empresa_id
    )

    db.add(cliente)
    db.commit()
    db.refresh(cliente)

    return cliente

# Func de listagem de clientes
def listar_clientes(
    empresa_id: int,
    db: Session,
    prioridade: Optional[PrioridadeEnum] = None, 
    data_inicio: Optional[datetime] = None,
    data_final: Optional[datetime] = None
):
    if data_final and not data_inicio:
        raise HTTPException(status_code=400, detail='Informa a data inicial junto da data final')

    query = db.query(Cliente).filter(Cliente.empresa_id == empresa_id)

    if prioridade:
        query = query.filter(Cliente.prioridade == prioridade)
    if data_inicio:
        query = query.filter(Cliente.created_at >= data_inicio)
    if data_final:
        query = query.filter(Cliente.created_at <= data_final)

    return query.all()

# Func de editar status do cliente
def editar_status_cliente(
        cliente_id: int,
        empresa_id: int,
        dados: ClienteUpdateStatus,
        db: Session
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail='Cliente não encontrado')
    
    if cliente.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail='Cliente não cadastrado na empresa')
    
    dados_update = dados.dict(exclude_unset=True)

    if dados_update.get('prioridade') == 'fechado' and not dados_update.get('valor_venda') and not cliente.valor_venda:
        raise HTTPException(status_code=400, detail='O valor da venda precisa ser declarado')
    
    for campo, valor in dados_update.items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)
    return cliente

# Func de edição de informações dos clientes
def editar_cliente(
    cliente_id: int,
    empresa_id: int,
    dados: ClienteInfoUpdate,
    db: Session
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail='Cliente não encontrado')
    
    if cliente.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail='Cliente não cadastrado na empresa')
    
    dados_update = dados.dict(exclude_unset=True)
    
    for campo, valor in dados_update.items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)

    return cliente

# Cadastro de clientes
@client_router.post('/cadastrar_cliente_usuario', response_model=ClienteResponse)
async def cadastrar_cliente_usuario(
    clienteschema: ClienteSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario)
    ):
    
    return cadastrar_cliente(clienteschema, usuario.empresa_id, db)

@client_router.post('/cadastrar_cliente_empresa', response_model=ClienteResponse)
async def cadastrar_cliente_empresa(
    clienteschema: ClienteSchema,
    db: Session = Depends(get_db),
    empresa: Empresa = Depends(get_current_empresa)
):
    return cadastrar_cliente(clienteschema, empresa.id, db)

# Listagem de clientes
@client_router.get('/listar_clientes_usuario', response_model=List[ClienteResponse])
async def listar_clientes_usuario(
    usuario: Usuario = Depends(get_current_usuario),
    db: Session = Depends(get_db),
    prioridade: Optional[PrioridadeEnum] = None,
    data_inicial: Optional[datetime] = None,
    data_final: Optional[datetime] = None
):
    return listar_clientes(usuario.empresa_id, db, prioridade, data_inicial, data_final)

@client_router.get('/listar_clientes_empresa', response_model=List[ClienteResponse])
async def listar_clientes_empresa(
    empresa: Empresa = Depends(get_current_empresa),
    db: Session = Depends(get_db),
    prioridade: Optional[PrioridadeEnum] = None,
    data_inicial: Optional[datetime] = None,
    data_final: Optional[datetime] = None
):
    return listar_clientes(empresa.id, db, prioridade, data_inicial, data_final)

# Listagem de cliente por ID
@client_router.get('/listar_clientes_usuario/{cliente_id}', response_model=ClienteResponse)
async def listar_clientes_usuario_id(
    cliente_id: int,
    usuario: Usuario = Depends(get_current_usuario),
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail='Cliente não encontrado')
    
    if cliente.empresa_id != usuario.empresa_id:
        raise HTTPException(status_code=403, detail='Cliente não cadastrado na empresa')
    
    return cliente

@client_router.get('/listar_clientes_empresa/{cliente_id}', response_model=ClienteResponse)
async def listar_clientes_empresa_id(
    cliente_id: int,
    empresa: Empresa = Depends(get_current_empresa),
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail='Cliente não encontrado')
    
    if cliente.empresa_id != empresa.id:
        raise HTTPException(status_code=403, detail='Usuário não cadastrado na empresa')
    
    return cliente

# Editar status de venda do cliente
@client_router.patch('/editar_status_cliente_usuario/{cliente_id}', response_model=ClienteResponse)
async def editar_usuario(
    cliente_id: int,
    dados: ClienteUpdateStatus,
    usuario: Usuario = Depends(get_current_usuario),
    db: Session = Depends(get_db)
):
    return editar_status_cliente(cliente_id, usuario.empresa_id, dados, db)

@client_router.patch('/editar_status_cliente_empresa/{cliente_id}', response_model=ClienteResponse)
async def editar_empresa(
    cliente_id: int,
    dados: ClienteUpdateStatus,
    empresa: Empresa = Depends(get_current_empresa),
    db: Session = Depends(get_db)
):
    return editar_status_cliente(cliente_id, empresa.id, dados, db)


# Editar Responsavel do cliente
@client_router.patch('/editar_responsavel_cliente/{cliente_id}', response_model=ClienteResponse)
async def editar_responsavel_cliente(
    cliente_id: int,
    usuario_id: ResponsavelClienteUpdate,
    empresa: Empresa = Depends(get_current_empresa),
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail='Cliente não encontrado')
    
    if cliente.empresa_id != empresa.id:
        raise HTTPException(status_code=403, detail='Cliente não cadastrado na empresa')
    
    responsavel = usuario_id.dict(exclude_unset=True)

    usuario = db.query(Usuario).filter(Usuario.id == responsavel.get('usuario_id')).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail='Funcionário não encontrado')
    if usuario.empresa_id != empresa.id:
        raise HTTPException(status_code=403, detail='Funcionário não pertence a empresa')

    for campo, valor in responsavel.items():
        setattr(cliente, campo, valor)
    
    db.commit()
    db.refresh(cliente)

    return cliente

# Editar os dados do cliente
@client_router.patch('/editar_cliente_usuario/{cliente_id}', response_model=ClienteResponse)
async def editar_cliente_usuario(
    cliente_id: int, 
    dados: ClienteInfoUpdate,
    usuario: Usuario = Depends(get_current_usuario),
    db: Session = Depends(get_db)
):
    return editar_cliente(cliente_id, usuario.empresa_id, dados, db)

@client_router.patch('/editar_cliente_empresa/{cliente_id}', response_model=ClienteResponse)
async def editar_cliente_empresa(
    cliente_id: int,
    dados: ClienteInfoUpdate,
    empresa: Empresa = Depends(get_current_empresa),
    db: Session = Depends(get_db)
):
    return editar_cliente(cliente_id, empresa.id, dados, db)