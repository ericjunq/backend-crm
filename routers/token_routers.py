from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db
from models.usuario_model import Usuario
from models.empresa_model import Empresa
from models.invite_token import TokenInvite
from security.security import get_current_empresa, get_current_usuario, gerar_token_invite
from schemas import TokenResponse, UsuarioVincularToken
from datetime import datetime, timezone, timedelta

token_router = APIRouter(prefix='/token', tags=['token'])

@token_router.post('/gerar_token', response_model=TokenResponse)
async def gerar_token(
    db: Session = Depends(get_db), 
    empresa: Empresa = Depends(get_current_empresa)
):
    expires = datetime.now(timezone.utc) + timedelta(hours=24)
    
    invite_token = TokenInvite(
        token = gerar_token_invite(),
        empresa_id = empresa.id,
        usado = False,
        expira_em = expires,
    )

    db.add(invite_token)
    db.commit()
    db.refresh(invite_token)

    return invite_token

@token_router.post('/vincular_token')
async def vincular_token(
    token_invite: UsuarioVincularToken, 
    db: Session = Depends(get_db), 
    usuario: Usuario = Depends(get_current_usuario)
    ):
    token = db.query(TokenInvite).filter(
        TokenInvite.token == token_invite.token
        ).first()
    
    if token is None:
        raise HTTPException(status_code=404, detail='Token de convite não encontrado')
    if token.expira_em < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail='Token de convite expirado')    
    if token.usado != False:
        raise HTTPException(status_code=400, detail='Token já utilizado')

    if usuario.empresa_id is not None:
        raise HTTPException(status_code=400, detail='Usuário já tem vinculo com empresa')

    usuario.empresa_id = token.empresa_id
    token.usado = True

    db.commit()
    db.refresh(usuario)
    
    return usuario