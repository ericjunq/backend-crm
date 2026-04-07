from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db
from fastapi.security import OAuth2PasswordRequestForm
from models.usuario_model import Usuario
from models.empresa_model import Empresa
from schemas import UsuarioSchema, UsuarioResponse, EmpresaSchema, EmpresaResponse, UsuarioUpdate, EmpresaUpdate
from security.security import criptografar_senha, verificar_senha, criar_access_token, get_current_usuario, criar_refresh_token, get_current_empresa

auth_router = APIRouter(prefix='/auth', tags=['auth'])

# Rota das cadastro
@auth_router.post('/cadastrar_empresa', response_model=EmpresaResponse)
async def cadastrar_empresa(empresaschema: EmpresaSchema, db: Session = Depends(get_db)):
    email_existente = db.query(Usuario).filter(Usuario.email == empresaschema.email).first()
    if email_existente:
        raise HTTPException(status_code=400, detail='Email já cadastrado')
    email_existente = db.query(Empresa).filter(Empresa.email == empresaschema.email).first()
    if email_existente:
        raise HTTPException(status_code=400, detail='Email já cadastrado')
    
    telefone_existente = db.query(Empresa).filter(Empresa.telefone == empresaschema.telefone).first()
    if telefone_existente:
        raise HTTPException(status_code=400, detail='Telefone já cadastrado')
    
    telefone_existente = db.query(Usuario).filter(Usuario.telefone == empresaschema.telefone).first()
    if telefone_existente:
        raise HTTPException(status_code=400, detail='Telefone já cadastrado')
    
    cnpj_existente = db.query(Empresa).filter(Empresa.cnpj == empresaschema.cnpj).first()
    if cnpj_existente:
        raise HTTPException(status_code=400, detail='CNPJ já cadastrado')
    
    senha_criptografada = criptografar_senha(empresaschema.senha)
    
    empresa = Empresa(
        nome = empresaschema.nome,
        email = empresaschema.email,
        senha_hash = senha_criptografada,
        cnpj = empresaschema.cnpj,
        telefone = empresaschema.telefone
    )

    db.add(empresa)
    db.commit()
    db.refresh(empresa)

    return empresa


@auth_router.post('/cadastrar_usuario')
async def cadastrar_usuario(usuarioschema: UsuarioSchema, db: Session = Depends(get_db)):
    email_existente = db.query(Usuario).filter(Usuario.email == usuarioschema.email).first()
    if email_existente:
        raise HTTPException(status_code=400, detail='Email já cadastrado')
    email_existente = db.query(Empresa).filter(Empresa.email == usuarioschema.email).first()
    if email_existente:
        raise HTTPException(status_code=400, detail='Email já cadastrado')
    
    telefone_existente = db.query(Empresa).filter(Empresa.telefone == usuarioschema.telefone).first()
    if telefone_existente:
        raise HTTPException(status_code=400, detail='Telefone já cadastrado')
    
    telefone_existente = db.query(Usuario).filter(Usuario.telefone == usuarioschema.telefone).first()
    if telefone_existente:
        raise HTTPException(status_code=400, detail='Telefone já cadastrado')
    
    cpf_existente = db.query(Usuario).filter(Usuario.cpf == usuarioschema.cpf).first()
    if cpf_existente:
        raise HTTPException(status_code=400, detail='CPF já cadastrado')
    
    senha_criptograda = criptografar_senha(usuarioschema.senha)

    usuario = Usuario(
        nome = usuarioschema.nome,
        sobrenome = usuarioschema.sobrenome,
        email = usuarioschema.email,
        senha_hash = senha_criptograda,
        cpf = usuarioschema.cpf,
        telefone = usuarioschema.telefone
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


# Rotas de Login
@auth_router.post('/login_empresa')
async def login_empresa(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    empresa = db.query(Empresa).filter(Empresa.email == form_data.username).first()
    if empresa is None:
        raise HTTPException(status_code=404, detail='Empresa inexistente')
    if not verificar_senha(form_data.password, empresa.senha_hash):
        raise HTTPException(status_code=401, detail='Senha incorreta')
    
    access_token = criar_access_token(
        dados={'sub': str(empresa.id), 'type': 'access', 'origin': 'empresa'}
    )

    refresh_token = criar_refresh_token(
        dados={'sub': str(empresa.id), 'type': 'refresh', 'origin': 'empresa'}
    )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }

@auth_router.post('/login_usuario')
async def login_usuario(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail='Usuário inexistente')
    if not verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail='Senha incorreta')
    
    access_token = criar_access_token(
        dados={'sub': str(usuario.id), 'type': 'access', 'origin': 'usuario'}
    )
    refresh_token = criar_refresh_token(
        dados={'sub': str(usuario.id), 'type': 'refresh', 'origin': 'usuario'}
    )
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }

# Rotas para editar dados
@auth_router.patch('/editar_empresa/', response_model=EmpresaResponse)
async def editar_empresa(
    dados: EmpresaUpdate, 
    db: Session = Depends(get_db), 
    empresa: Empresa = Depends(get_current_empresa)
):
    dados_update = dados.dict(exclude_unset=True)

    if 'email' in dados_update:
        email_existente_empresa = db.query(Empresa).filter(
            Empresa.email == dados_update['email']
            ).first()
        
        email_existente_usuario = db.query(Usuario).filter(
            Usuario.email == dados_update['email']
            ).first()
        
        if (email_existente_empresa and email_existente_empresa.id != empresa.id) or email_existente_usuario:
            raise HTTPException(status_code=400, detail='Email já cadastrado')

    if 'telefone' in dados_update:
        telefone_existente_empresa = db.query(Empresa).filter(
            Empresa.telefone == dados_update['telefone']
            ).first()
        
        telefone_existente_usuario = db.query(Usuario).filter(
            Usuario.telefone == dados_update['telefone']
        ).first()
        
        if (telefone_existente_empresa and telefone_existente_empresa.id != empresa.id) or telefone_existente_usuario:
            raise HTTPException(status_code=400, detail='Telefone já cadastrado')
        
    if 'senha' in dados_update:
        dados_update['senha_hash'] = criptografar_senha(dados_update.pop('senha'))
        
    for campo, valor in dados_update.items():
        setattr(empresa, campo, valor)
    
    db.commit()
    db.refresh(empresa)

    return empresa

@auth_router.patch('/editar_usuario/', response_model=UsuarioResponse)
async def editar_usuario(
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario)
):
    dados_update = dados.dict(exclude_unset=True)

    if 'email' in dados_update:
        email_existente_usuario = db.query(Usuario).filter(
            Usuario.email == dados_update['email']
            ).first()
        
        email_existente_empresa = db.query(Empresa).filter(
            Empresa.email == dados_update['email']
        ).first()

        if (email_existente_usuario and email_existente_usuario.id != usuario.id) or email_existente_empresa:
            raise HTTPException(status_code=400, detail='Email já cadastrado')
        
    if 'telefone' in dados_update:
        telefone_existente_usuario = db.query(Usuario).filter(
            Usuario.telefone == dados_update['telefone']
        ).first()

        telefone_existente_empresa = db.query(Empresa).filter(
            Empresa.telefone == dados_update['telefone']
        ).first()

        if (telefone_existente_usuario and telefone_existente_usuario.id != usuario.id) or telefone_existente_empresa:
            raise HTTPException(status_code=400, detail='Telefone já cadastrado')
    
    if 'senha' in dados_update:
        dados_update['senha_hash'] = criptografar_senha(dados_update.pop('senha'))

        
    for campo, valor in dados_update.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)

    return usuario