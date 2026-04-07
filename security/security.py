from pwdlib import PasswordHash
from jose import jwt, JWTError
from database import settings
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from dependencies import get_db
from sqlalchemy.orm import Session
from models.empresa_model import Empresa
from models.usuario_model import Usuario
import secrets

password_hash = PasswordHash.recommended()
oauth_empresa = OAuth2PasswordBearer(tokenUrl='/auth/empresa/login_empresa')
oauth_usuario = OAuth2PasswordBearer(tokenUrl='/auth/usuario/login_usuario')

def criptografar_senha(senha: str) -> str:
    return password_hash.hash(senha)

def verificar_senha(senha: str, senha_hash: str) -> str:
    return password_hash.verify(senha, senha_hash)


def criar_access_token(dados: dict):
    to_encode = dados.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expires_minutes)
    to_encode.update({'exp': expire})

    access_token = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return access_token

def criar_refresh_token(dados: dict):
    to_encode = dados.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expires_days)
    to_encode.update({'exp': expire})

    refresh_token = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return refresh_token

def get_current_empresa(token: str = Depends(oauth_empresa), db: Session = Depends(get_db)):
    try:    
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        origem = payload.get('origin')
        if origem != 'empresa':
            raise HTTPException(status_code=401, detail='Token inválido')

        empresa_id = payload.get('sub')
        if empresa_id is None:
            raise HTTPException(status_code=401, detail='Token inválido')
    except JWTError:
        raise HTTPException(status_code=401, detail='Token inválido')
    
    empresa = db.query(Empresa).filter(Empresa.id == int(empresa_id)).first()
    if not empresa:
        raise HTTPException(status_code=401, detail='Empresa não encontrada')
    
    return empresa

def get_current_usuario(token: str = Depends(oauth_usuario), db: Session = Depends(get_db)):
    try:    
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        origem = payload.get('origin')
        if origem != 'usuario':
            raise HTTPException(status_code=401, detail='Token inválido')

        usuario_id = payload.get('sub')
        if usuario_id is None:
            raise HTTPException(status_code=401, detail='Token inválido')
    except JWTError:
        raise HTTPException(status_code=401, detail='Token inválido')
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=401, detail='Usuario não encontrada')
    
    return usuario

def gerar_token_invite()-> str:
    return secrets.token_urlsafe(16)