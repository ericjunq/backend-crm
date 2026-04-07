from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas import RelatorioResponse
from models.interacao import Interacao
from models.cliente_model import Cliente
from models.empresa_model import Empresa
from security.security import get_current_empresa
from enums import FormatoDownload, DataFilterEnum
from typing import List
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
import pandas as pd
import io

relatorio_router = APIRouter(prefix='/relatorios', tags=['relatorios'])

# Func de filtragem por periodo
def calcular_periodo(
    data_filter: DataFilterEnum
):
    agora = datetime.now(timezone.utc)
    if data_filter.value == 'dia':
        inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
        return inicio
    elif data_filter.value == 'semana':
        inicio = (agora - timedelta(days=7)).replace(hour=0, minute=0,second=0,microsecond=0)
        return inicio
    elif data_filter.value == 'mes':
        inicio = agora.replace(day=1, hour=0, minute=0, second= 0, microsecond= 0)           
        return inicio
    elif data_filter.value == 'trimestre':
        mes_atual = agora.month
        inicio_trimestre = ((mes_atual-1) // 3) * 3 + 1     
        inicio = agora.replace(month=inicio_trimestre, day=1, hour= 0, minute=0, second=0, microsecond=0)    
        return inicio
    elif data_filter.value == 'semestre':
        if agora.month <= 6:
            inicio = agora.replace(month=1, day=1, hour= 0, minute=0, second=0, microsecond=0)
        else:
                inicio = agora.replace(month=7, day=1, hour= 0, minute=0, second=0, microsecond=0)
        return inicio
    elif data_filter.value == 'ano':
        inicio = agora.replace(month=1,day=1,hour=0,minute=0,second=0,microsecond=0)
        return inicio

# Func para filtragem de dados pro relatório   
def relatorio(
    periodo: DataFilterEnum,
    db: Session,
    empresa_id: int
):
    clientes = db.query(Cliente).filter(
        Cliente.empresa_id == empresa_id,
        Cliente.created_at >= calcular_periodo(periodo)
        ).count()
    
    interacoes = db.query(Interacao).join(Cliente).filter(
        Cliente.empresa_id == empresa_id,
        Interacao.created_at >= calcular_periodo(periodo)
    ).count()
    
    vendas = db.query(Cliente).filter(
        Cliente.prioridade == 'fechado',
        Cliente.empresa_id == empresa_id,
        Cliente.created_at >= calcular_periodo(periodo)
        ).count()
    
    faturamento = db.query(func.sum(Cliente.valor_venda)).filter(
        Cliente.empresa_id == empresa_id,
        Cliente.prioridade == 'fechado',
        Cliente.created_at >= calcular_periodo(periodo),
    ).scalar()

    if faturamento is None:
        faturamento = 0.0
    
    if clientes != 0:
        taxa_conversao = (vendas / clientes) * 100
    else:
        taxa_conversao = 0.0

    dados = {
        'total_clientes': clientes,
        'total_interacoes': interacoes,
        'total_vendas': vendas,
        'faturamento_total': faturamento,
        'taxa_conversao': taxa_conversao,
        'periodo': periodo
    }
    return dados

@relatorio_router.get('/relatorios', response_model=RelatorioResponse)
async def gerar_relatorio(
    periodo: DataFilterEnum,
    db: Session = Depends(get_db),
    empresa: Empresa = Depends(get_current_empresa)
):
    return relatorio(periodo, db, empresa.id)

@relatorio_router.get('/relatorios/download')
async def gerar_relatorio_download(
    formato: FormatoDownload,
    periodo: DataFilterEnum,
    db: Session = Depends(get_db),
    empresa: Empresa = Depends(get_current_empresa)
):
    df = pd.DataFrame([relatorio(periodo, db, empresa.id)])
    if formato == FormatoDownload.excel:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Relatorio')
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename=relatorio_{periodo.value}.xlsx'}
        )
    if formato == FormatoDownload.csv:
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False, encoding='utf-8-sig')
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename=relatorio_{periodo.value}.csv'}
        )    
    else:
        raise HTTPException(status_code=400, detail='Formato não suportado')