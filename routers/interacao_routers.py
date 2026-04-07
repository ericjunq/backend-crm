from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas import InteracaoSchema, InteracaoResponse, InteracaoFilter
from models.interacao import Interacao
from models.cliente_model import Cliente
from models.usuario_model import Usuario
from models.empresa_model import Empresa
from typing import Optional, List
from security.security import get_current_empresa, get_current_usuario
from enums import DataFilterEnum
from datetime import datetime, timedelta, timezone, date

interacao_router = APIRouter(prefix='/interacoes', tags=['interacoes'])

# Cria interacao
def criar_interacao(
        cliente_id: int, 
        empresa_id: int,
        dados: InteracaoSchema,
        db: Session,
        usuario_id: Optional[int] = None,
        empresa_criou_id: Optional[int] = None
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail='Cliente não encontrado')
    
    if cliente.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail='Cliente não pertence a empresa')
    
    interacao = Interacao(
        tipo = dados.tipo,
        descricao = dados.descricao,
        cliente_id = cliente_id, 
        usuario_id = usuario_id,
        empresa_id = empresa_criou_id
    )

    db.add(interacao)
    db.commit()
    db.refresh(interacao)

    return interacao

def listar_interacoes_cliente(
    cliente_id: int,
    empresa_id: int,
    db: Session,
    data_filter: Optional[InteracaoFilter] = None
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail='Cliente não encontrado')
    
    if cliente.empresa_id != empresa_id:
        raise HTTPException(status_code=403, detail='Cliente não cadastrado na empresa')


    query = db.query(Interacao).filter(Interacao.cliente_id == cliente.id)

    if data_filter:
        agora = datetime.now(timezone.utc)
        if data_filter.value == 'dia':
            inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
            fim = inicio + timedelta(days=1)
            query = query.filter(Interacao.created_at >= inicio, Interacao.created_at < fim)
        elif data_filter.value == 'semana':
            inicio = (agora - timedelta(days=7)).replace(hour=0, minute=0,second=0,microsecond=0)
            query = query.filter(Interacao.created_at >= inicio)
        elif data_filter.value == 'mes':
            inicio = agora.replace(day=1, hour=0, minute=0, second= 0, microsecond= 0)           
            query = query.filter(Interacao.created_at >= inicio)
        elif data_filter.value == 'trimestre':
            mes_atual = agora.month
            inicio_trimestre = ((mes_atual-1) // 3) * 3 + 1     
            inicio = agora.replace(month=inicio_trimestre, day=1, hour= 0, minute=0, second=0, microsecond=0)    
            query = query.filter(Interacao.created_at >= inicio)
        elif data_filter.value == 'semestre':
            if agora.month <= 6:
                inicio = agora.replace(month=1, day=1, hour= 0, minute=0, second=0, microsecond=0)
            else:
                inicio = agora.replace(month=7, day=1, hour= 0, minute=0, second=0, microsecond=0)
            query = query.filter(Interacao.created_at >= inicio)
        elif data_filter.value == 'ano':
            inicio = agora.replace(month=1,day=1,hour=0,minute=0,second=0,microsecond=0)
            query = query.filter(Interacao.created_at >= inicio)
        
    return query.all()

# Criam interacao
@interacao_router.post('/criar_interacao_usuario', response_model=InteracaoResponse)
async def criar_interacao_usuario(
    cliente_id: int, 
    dados: InteracaoSchema,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario)
):
    return criar_interacao(cliente_id, usuario.empresa_id, dados, db, usuario.id)

@interacao_router.post('/criar_interacao_empresa', response_model=InteracaoResponse)
async def criar_interacao_empresa(
    cliente_id: int,
    dados: InteracaoSchema,
    db: Session = Depends(get_db),
    empresa: Empresa = Depends(get_current_empresa)
):
    return criar_interacao(cliente_id, empresa.id, dados, db, empresa_criou_id=empresa.id)

# Rotas de filtragem
@interacao_router.get('/filtrar_interacao_usuario/{cliente_id}', response_model=List[InteracaoResponse])
async def listar_interacao_clientes_usuario(
    cliente_id: int,
    filtro: Optional[InteracaoFilter] = None,
    usuario: Usuario = Depends(get_current_usuario),
    db: Session = Depends(get_db)
):
    return listar_interacoes_cliente(cliente_id, usuario.empresa_id, db, filtro)

@interacao_router.get('/filtrar_interacao_empresa/{cliente_id}', response_model=List[InteracaoResponse])
async def listar_interacao_clientes_empresa(
    cliente_id: int, 
    filtro: Optional[InteracaoFilter] = None,
    empresa: Empresa = Depends(get_current_empresa),
    db: Session = Depends(get_db)
):
    return listar_interacoes_cliente(cliente_id, empresa.id, db, filtro)

# Para implementar -> Filtragem de interações de clientes criados por : Usuario/Empresa

@interacao_router.delete('/deletar_interacao/{interacao_id}')
async def deletar_interacao(
    interacao_id: int, 
    db: Session = Depends(get_db),
    empresa: Empresa = Depends(get_current_empresa)
):
    interacao = db.query(Interacao).filter(Interacao.id == interacao_id).first()
    if interacao is None:
        raise HTTPException(status_code=404, detail='Interação não encontrada')
    
    cliente = db.query(Cliente).filter(
        Cliente.id == interacao.cliente_id, 
        Cliente.empresa_id == empresa.id
    ).first()
    if cliente is None:
        raise HTTPException(status_code=403, detail='Sem permissão para deletar essa interação')
    
    db.delete(interacao)
    db.commit()

    return {'System response': 'Interação deletada com sucesso'}
