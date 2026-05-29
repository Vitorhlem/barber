import os
import uuid
import base64
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, List
import shutil
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

import models
import schemas
from database import engine, get_db

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="BarberBase API - SaaS")
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# --- VARIÁVEIS DE AMBIENTE (Automático Local vs Produção) ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")

# --- DEPENDÊNCIA: ISOLAMENTO POR BARBEARIA (SaaS) ---
def obter_barbearia(slug: str, db: Session = Depends(get_db)):
    barbearia = db.query(models.Barbearia).filter(models.Barbearia.slug == slug).first()
    if not barbearia:
        raise HTTPException(status_code=404, detail="Barbearia não encontrada. Verifique o link.")
    if not barbearia.ativa:
        raise HTTPException(status_code=403, detail="Esta barbearia está inativa.")
    return barbearia


@app.post("/upload/imagem")
async def upload_imagem(file: UploadFile = File(...)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Usa variável de ambiente para decidir se é localhost ou domínio oficial
    return {"url": f"{API_BASE_URL}/uploads/{file.filename}"}

# --- GERENCIADOR DE WEB SOCKETS ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)
                
    async def broadcast_update(self, user_id: int, action: str):
        msg = json.dumps({"action": action, "timestamp": datetime.utcnow().isoformat()})
        await self.send_personal_message(msg, user_id)

manager = ConnectionManager()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173", "http://barber.ravitex.com.br", "https://barber.ravitex.com.br"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- FUNÇÕES DE APOIO GOOGLE ---
auth_state_store = {}

def get_valid_creds(token_entry):
    creds = Credentials(
        token=token_entry.access_token,
        refresh_token=token_entry.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID", "SEU_ID_AQUI"), 
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", "SEU_SECRET_AQUI")
    )
    if creds.expired:
        creds.refresh(GoogleRequest())
    return creds

def criar_evento_google(token_entry, agendamento, db):
    creds = get_valid_creds(token_entry)
    service = build('calendar', 'v3', credentials=creds)
    
    evento = {
        'summary': f'Atendimento: {agendamento.servico}',
        'description': f'Cliente: {agendamento.cliente_nome}',
        'start': {'dateTime': agendamento.data_hora.isoformat(), 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': (agendamento.data_hora + timedelta(minutes=30)).isoformat(), 'timeZone': 'America/Sao_Paulo'},
    }
    
    evento_criado = service.events().insert(calendarId='primary', body=evento).execute()
    agendamento.google_event_id = evento_criado.get('id')
    db.commit()


# --- ROTA SUPER ADMIN (Criar Barbearias) ---
@app.post("/admin/barbearias/")
def criar_barbearia(nome: str, slug: str, usuario_logado_id: int, admin_nome: str, admin_email: str, admin_senha: str, db: Session = Depends(get_db)):
    # 1. Verifica se quem está criando é realmente o Super Admin
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_logado_id).first()
    if not usuario or usuario.tipo != "admin" or usuario.barbearia_id != 1:
        raise HTTPException(status_code=403, detail="Acesso negado: Apenas o Super Admin pode criar novas lojas.")

    # 2. Verifica se a loja já existe
    existe = db.query(models.Barbearia).filter(models.Barbearia.slug == slug).first()
    if existe:
        raise HTTPException(status_code=400, detail="Já existe uma loja com este link/slug.")
        
    # 3. Verifica se o e-mail do novo dono já está em uso
    email_existe = db.query(models.Usuario).filter(models.Usuario.email == admin_email).first()
    if email_existe:
        raise HTTPException(status_code=400, detail="Este e-mail já está sendo usado por outro usuário.")
    
    # 4. Cria a loja
    nova_barbearia = models.Barbearia(nome=nome, slug=slug)
    db.add(nova_barbearia)
    db.commit()
    db.refresh(nova_barbearia)
    
    # 5. Cria o dono da loja (Admin local) vinculado à loja recém-criada
    novo_dono = models.Usuario(
        nome=admin_nome,
        email=admin_email,
        senha_hash=admin_senha,
        tipo="barbeiro",
        telefone="",
        barbearia_id=nova_barbearia.id
    )
    db.add(novo_dono)
    db.commit()
    
    return {
        "message": "Barbearia e Dono criados com sucesso", 
        "barbearia": nova_barbearia.nome, 
        "link": f"{FRONTEND_URL}/{nova_barbearia.slug}/login"
    }
# --- ROTAS DE AUTENTICAÇÃO ---
@app.get("/{slug}/auth/google/login")
async def login_google(slug: str, user_id: int):
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode().replace("=", "")
    state_id = str(uuid.uuid4())
    
    auth_state_store[state_id] = {"user_id": user_id, "code_verifier": code_verifier, "slug": slug}
    
    flow = Flow.from_client_secrets_file("client_secret.json", scopes=['https://www.googleapis.com/auth/calendar'], redirect_uri=GOOGLE_REDIRECT_URI)
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', state=state_id, code_challenge=code_challenge, code_challenge_method='S256')
    return {"url": auth_url}

@app.get("/auth/callback")
async def oauth2_callback(code: str, state: str, db: Session = Depends(get_db)):
    data = auth_state_store.get(state)
    if not data:
        raise HTTPException(status_code=400, detail="Pedido inválido.")
    
    user_id = data["user_id"]
    code_verifier = data["code_verifier"]
    slug = data.get("slug", "") 
    del auth_state_store[state]

    flow = Flow.from_client_secrets_file("client_secret.json", scopes=['https://www.googleapis.com/auth/calendar'], redirect_uri=GOOGLE_REDIRECT_URI)
    flow.fetch_token(code=code, code_verifier=code_verifier)
    creds = flow.credentials

    token_entry = db.query(models.GoogleToken).filter(models.GoogleToken.user_id == user_id).first()
    
    if not token_entry:
        token_entry = models.GoogleToken(user_id=user_id)
        db.add(token_entry)
    
    token_entry.access_token = creds.token
    token_entry.refresh_token = creds.refresh_token
    token_entry.token_expiry = creds.expiry
    db.commit()
    
    return RedirectResponse(url=f"{FRONTEND_URL}/{data.get('slug')}/dashboard")

# --- ROTAS DE USUÁRIOS E AGENDAMENTOS ---
@app.post("/{slug}/usuarios/", response_model=schemas.UsuarioResponse)
def criar_usuario(slug: str, usuario: schemas.UsuarioCreate, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_usuario = models.Usuario(
        nome=usuario.nome, 
        email=usuario.email, 
        senha_hash=usuario.senha, 
        tipo=usuario.tipo, 
        telefone=usuario.telefone,
        barbearia_id=barbearia.id 
    )
    db.add(db_usuario)
    try:
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="E-mail já cadastrado nesta plataforma.")

@app.post("/{slug}/login/", response_model=schemas.UsuarioResponse)
def login(slug: str, usuario: schemas.UsuarioLogin, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_usuario = db.query(models.Usuario).filter(
        models.Usuario.email == usuario.email,
        models.Usuario.barbearia_id == barbearia.id 
    ).first()
    if not db_usuario or db_usuario.senha_hash != usuario.senha:
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos para esta barbearia")
    return db_usuario

@app.post("/{slug}/usuarios/{cliente_id}/agendamentos", response_model=schemas.AgendamentoResponse)
async def criar_agendamento(slug: str, cliente_id: int, agendamento: schemas.AgendamentoCreate, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_agendamento = models.Agendamento(**agendamento.model_dump(), cliente_id=cliente_id, barbearia_id=barbearia.id)
    db.add(db_agendamento)
    db.commit()
    db.refresh(db_agendamento)
    
    await manager.broadcast_update(agendamento.barbeiro_id, "UPDATE_AGENDAMENTOS")
    await manager.broadcast_update(cliente_id, "UPDATE_AGENDAMENTOS")
    
    token_db = db.query(models.GoogleToken).filter(models.GoogleToken.user_id == agendamento.barbeiro_id).first()
    if token_db:
        try:
            criar_evento_google(token_db, db_agendamento, db)
        except Exception as e:
            print(f"DEBUG CRÍTICO: Falha ao criar evento no Google: {e}")
            
    return db_agendamento

@app.get("/{slug}/agendamentos/barbeiro/{barbeiro_id}", response_model=List[schemas.AgendamentoResponse])
def listar_agendamentos(slug: str, barbeiro_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    return db.query(models.Agendamento).options(
        joinedload(models.Agendamento.cliente),
        joinedload(models.Agendamento.barbeiro)
    ).filter(
        models.Agendamento.barbeiro_id == barbeiro_id,
        models.Agendamento.barbearia_id == barbearia.id
    ).all()

@app.put("/{slug}/agendamentos/{agendamento_id}", response_model=schemas.AgendamentoResponse)
async def atualizar(slug: str, agendamento_id: int, agendamento_update: schemas.AgendamentoUpdate, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_agendamento = db.query(models.Agendamento).filter(
        models.Agendamento.id == agendamento_id,
        models.Agendamento.barbearia_id == barbearia.id
    ).first()
    db_agendamento.status = agendamento_update.status
    db.commit()
    db.refresh(db_agendamento)
    
    await manager.broadcast_update(db_agendamento.cliente_id, "UPDATE_AGENDAMENTOS")
    await manager.broadcast_update(db_agendamento.barbeiro_id, "UPDATE_AGENDAMENTOS")
    
    return db_agendamento

@app.delete("/{slug}/agendamentos/{agendamento_id}")
async def deletar_agendamento(slug: str, agendamento_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_agendamento = db.query(models.Agendamento).filter(
        models.Agendamento.id == agendamento_id,
        models.Agendamento.barbearia_id == barbearia.id
    ).first()
    if not db_agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    if db_agendamento.google_event_id:
        token_db = db.query(models.GoogleToken).filter(models.GoogleToken.user_id == db_agendamento.barbeiro_id).first()
        if token_db:
            try:
                creds = get_valid_creds(token_db)
                service = build('calendar', 'v3', credentials=creds)
                service.events().delete(calendarId='primary', eventId=db_agendamento.google_event_id).execute()
            except Exception:
                pass

    cliente_id = db_agendamento.cliente_id
    barbeiro_id = db_agendamento.barbeiro_id

    db.delete(db_agendamento)
    db.commit()
    
    await manager.broadcast_update(cliente_id, "UPDATE_AGENDAMENTOS")
    await manager.broadcast_update(barbeiro_id, "UPDATE_AGENDAMENTOS")
    
    return {"message": "Agendamento cancelado"}

@app.get("/{slug}/agendamentos/{agendamento_id}", response_model=schemas.AgendamentoResponse)
def buscar_agendamento(slug: str, agendamento_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    agendamento = db.query(models.Agendamento).options(
        joinedload(models.Agendamento.cliente),
        joinedload(models.Agendamento.barbeiro)
    ).filter(
        models.Agendamento.id == agendamento_id,
        models.Agendamento.barbearia_id == barbearia.id 
    ).first()
    
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        
    return agendamento

@app.put("/{slug}/usuarios/{user_id}/alterar-senha")
def alterar_senha(slug: str, user_id: int, dados: schemas.AlterarSenhaRequest, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == user_id, models.Usuario.barbearia_id == barbearia.id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    if usuario.senha_hash != dados.senha_atual:
        raise HTTPException(status_code=400, detail="A senha atual informada está incorreta.")
        
    usuario.senha_hash = dados.nova_senha
    db.commit()
    return {"message": "Senha alterada com sucesso."}


# --- ROTA: ALTERAR SLUG/LINK DA BARBEARIA (CRÍTICO) ---
@app.put("/{slug}/sistema/alterar-slug")
def alterar_slug(slug: str, dados: schemas.AlterarSlugRequest, usuario_logado_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    
    # 1. Busca o usuário no banco para garantir que ele pertence a esta barbearia
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_logado_id, models.Usuario.barbearia_id == barbearia.id).first()

    # 2. VERIFICAÇÃO DE SEGURANÇA: Checa se o usuário existe e se é admin ou barbeiro
    if not usuario or usuario.tipo not in ["admin", "barbeiro"]:
        raise HTTPException(
            status_code=403, 
            detail="Acesso negado. Apenas administradores ou membros da equipe podem alterar o link da loja."
        )

    # 3. Formata o novo link (slug)
    novo_slug_formatado = dados.novo_slug.strip().lower().replace(" ", "-")
    
    if not novo_slug_formatado:
        raise HTTPException(status_code=400, detail="O link não pode ficar em branco.")
        
    if novo_slug_formatado == slug:
        return {"message": "O link informado já é o link atual desta loja.", "novo_slug": slug}

    # 4. Verifica se o novo link já está sendo usado por outra loja
    existe = db.query(models.Barbearia).filter(models.Barbearia.slug == novo_slug_formatado).first()
    if existe:
        raise HTTPException(status_code=400, detail="Este link de acesso já está em uso por outra barbearia. Escolha outro.")
    
    # 5. Salva a alteração
    barbearia.slug = novo_slug_formatado
    db.commit()
    db.refresh(barbearia)
    
    return {"message": "Link da barbearia alterado com sucesso!", "novo_slug": barbearia.slug}
@app.get("/{slug}/usuarios/{cliente_id}/agendamentos")
def listar_agendamentos_cliente(slug: str, cliente_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    return db.query(models.Agendamento).options(
        joinedload(models.Agendamento.cliente),
        joinedload(models.Agendamento.barbeiro)
    ).filter(
        models.Agendamento.cliente_id == cliente_id,
        models.Agendamento.barbearia_id == barbearia.id
    ).all()

@app.get("/{slug}/barbeiros/", response_model=List[schemas.UsuarioResponse])
def listar_barbeiros(slug: str, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    return db.query(models.Usuario).filter(
        models.Usuario.tipo == "barbeiro",
        models.Usuario.barbearia_id == barbearia.id
    ).all()

# --- BLOQUEIOS DE HORÁRIOS ---
@app.post("/{slug}/bloqueios/", response_model=schemas.BloqueioResponse)
async def criar_bloqueio(slug: str, bloqueio: schemas.BloqueioCreate, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_bloqueio = models.BloqueioHorario(**bloqueio.model_dump(), barbearia_id=barbearia.id)
    db.add(db_bloqueio)
    db.commit()
    db.refresh(db_bloqueio)
    await manager.broadcast_update(bloqueio.barbeiro_id, "UPDATE_BLOQUEIOS")
    return db_bloqueio

@app.get("/{slug}/bloqueios/barbeiro/{barbeiro_id}", response_model=List[schemas.BloqueioResponse])
def listar_bloqueios(slug: str, barbeiro_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    return db.query(models.BloqueioHorario).filter(
        models.BloqueioHorario.barbeiro_id == barbeiro_id,
        models.BloqueioHorario.barbearia_id == barbearia.id
    ).all()

@app.delete("/{slug}/bloqueios/{bloqueio_id}")
async def deletar_bloqueio(slug: str, bloqueio_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_bloqueio = db.query(models.BloqueioHorario).filter(
        models.BloqueioHorario.id == bloqueio_id,
        models.BloqueioHorario.barbearia_id == barbearia.id
    ).first()
    if not db_bloqueio:
        raise HTTPException(status_code=404, detail="Bloqueio não encontrado")
    
    barbeiro_id = db_bloqueio.barbeiro_id
    db.delete(db_bloqueio)
    db.commit()
    
    await manager.broadcast_update(barbeiro_id, "UPDATE_BLOQUEIOS")
    return {"message": "Bloqueio removido"}

@app.get("/{slug}/folgas/barbeiro/{barbeiro_id}", response_model=List[schemas.FolgaPontualResponse])
def listar_folgas(slug: str, barbeiro_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    return db.query(models.FolgaPontual).filter(
        models.FolgaPontual.barbeiro_id == barbeiro_id,
        models.FolgaPontual.barbearia_id == barbearia.id
    ).all()

@app.post("/{slug}/folgas/", response_model=schemas.FolgaPontualResponse)
async def criar_folga(slug: str, folga: schemas.FolgaPontualCreate, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_folga = models.FolgaPontual(**folga.model_dump(), barbearia_id=barbearia.id)
    db.add(db_folga)
    db.commit()
    db.refresh(db_folga)
    await manager.broadcast_update(folga.barbeiro_id, "UPDATE_FOLGAS")
    return db_folga

@app.delete("/{slug}/folgas/{folga_id}")
async def deletar_folga(slug: str, folga_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_folga = db.query(models.FolgaPontual).filter(
        models.FolgaPontual.id == folga_id,
        models.FolgaPontual.barbearia_id == barbearia.id
    ).first()
    if not db_folga:
        raise HTTPException(status_code=404, detail="Folga não encontrada")
    barbeiro_id = db_folga.barbeiro_id
    db.delete(db_folga)
    db.commit()
    await manager.broadcast_update(barbeiro_id, "UPDATE_FOLGAS")
    return {"message": "Folga removida com sucesso"}

# --- SERVIÇOS E PRODUTOS (Por Loja) ---
@app.get("/{slug}/servicos/", response_model=List[schemas.ServicoResponse])
def listar_servicos(slug: str, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    servicos = db.query(models.Servico).filter(models.Servico.barbearia_id == barbearia.id).all()
    if not servicos:
        padroes = [
            {"nome": "Corte de Cabelo", "preco": 15.00},
            {"nome": "Barba", "preco": 10.00},
            {"nome": "Corte + Barba", "preco": 23.00}
        ]
        for p in padroes:
            db.add(models.Servico(**p, barbearia_id=barbearia.id))
        db.commit()
        servicos = db.query(models.Servico).filter(models.Servico.barbearia_id == barbearia.id).all()
    return servicos

@app.post("/{slug}/servicos/", response_model=schemas.ServicoResponse)
def salvar_ou_atualizar_servico(slug: str, servico: schemas.ServicoCreate, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_servico = db.query(models.Servico).filter(
        models.Servico.nome == servico.nome,
        models.Servico.barbearia_id == barbearia.id
    ).first()
    
    if db_servico:
        db_servico.preco = servico.preco
    else:
        db_servico = models.Servico(**servico.model_dump(), barbearia_id=barbearia.id)
        db.add(db_servico)
    db.commit()
    db.refresh(db_servico)
    return db_servico

@app.delete("/{slug}/servicos/{servico_id}")
def deletar_servico(slug: str, servico_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_servico = db.query(models.Servico).filter(
        models.Servico.id == servico_id,
        models.Servico.barbearia_id == barbearia.id
    ).first()
    if not db_servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    db.delete(db_servico)
    db.commit()
    return {"message": "Serviço removido"}

@app.get("/{slug}/produtos/", response_model=List[schemas.ProdutoResponse])
def listar_produtos(slug: str, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    return db.query(models.Produto).filter(models.Produto.barbearia_id == barbearia.id).all()

@app.post("/{slug}/produtos/", response_model=schemas.ProdutoResponse)
def criar_produto(slug: str, produto: schemas.ProdutoCreate, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_produto = models.Produto(**produto.model_dump(), barbearia_id=barbearia.id)
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

@app.delete("/{slug}/produtos/{produto_id}")
def deletar_produto(slug: str, produto_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    db_produto = db.query(models.Produto).filter(
        models.Produto.id == produto_id,
        models.Produto.barbearia_id == barbearia.id
    ).first()
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(db_produto)
    db.commit()
    return {"message": "Produto removido"}

# --- CONFIGURAÇÃO E DADOS DA BARBEARIA (Substituindo ConfiguracaoSistema) ---
@app.get("/{slug}/sistema/config")
def obter_configuracao_sistema(slug: str, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    return {
        "nome_barbearia": barbearia.nome,
        "logo_url": barbearia.logo_url
    }

@app.put("/{slug}/sistema/config")
def atualizar_configuracao_sistema(slug: str, config_update: schemas.ConfiguracaoSistemaBase, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    barbearia.nome = config_update.nome_barbearia
    barbearia.logo_url = config_update.logo_url
    db.commit()
    db.refresh(barbearia)
    return {
        "nome_barbearia": barbearia.nome,
        "logo_url": barbearia.logo_url
    }

# --- ROTAS DE CONFIGURAÇÃO DE HORÁRIO DO BARBEIRO ---
@app.get("/{slug}/configuracao/{barbeiro_id}", response_model=schemas.ConfiguracaoBarbeiroResponse)
def obter_configuracao(slug: str, barbeiro_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    config = db.query(models.ConfiguracaoBarbeiro).filter(
        models.ConfiguracaoBarbeiro.barbeiro_id == barbeiro_id,
        models.ConfiguracaoBarbeiro.barbearia_id == barbearia.id
    ).first()
    
    if not config:
        default_horarios = [
            {"dia": 0, "nome": "Domingo", "trabalha": False, "inicio": "08:00", "fim": "12:00"},
            {"dia": 1, "nome": "Segunda-feira", "trabalha": True, "inicio": "08:00", "fim": "18:00"},
            {"dia": 2, "nome": "Terça-feira", "trabalha": True, "inicio": "08:00", "fim": "18:00"},
            {"dia": 3, "nome": "Quarta-feira", "trabalha": True, "inicio": "08:00", "fim": "18:00"},
            {"dia": 4, "nome": "Quinta-feira", "trabalha": True, "inicio": "08:00", "fim": "18:00"},
            {"dia": 5, "nome": "Sexta-feira", "trabalha": True, "inicio": "08:00", "fim": "18:00"},
            {"dia": 6, "nome": "Sábado", "trabalha": True, "inicio": "08:00", "fim": "18:00"}
        ]
        config = models.ConfiguracaoBarbeiro(
            barbeiro_id=barbeiro_id,
            barbearia_id=barbearia.id,
            intervalo_minutos=30,
            horarios_json=json.dumps(default_horarios),
            loja_aberta=True
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

@app.put("/{slug}/configuracao/{barbeiro_id}", response_model=schemas.ConfiguracaoBarbeiroResponse)
def atualizar_configuracao(slug: str, barbeiro_id: int, config_update: schemas.ConfiguracaoBarbeiroUpdate, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    
    config = db.query(models.ConfiguracaoBarbeiro).filter(
        models.ConfiguracaoBarbeiro.barbeiro_id == barbeiro_id,
        models.ConfiguracaoBarbeiro.barbearia_id == barbearia.id
    ).first()
    
    if not config:
        config = models.ConfiguracaoBarbeiro(barbeiro_id=barbeiro_id, barbearia_id=barbearia.id)
        db.add(config)
    
    config.intervalo_minutos = config_update.intervalo_minutos
    config.horarios_json = config_update.horarios_json
    config.loja_aberta = config_update.loja_aberta
    
    db.commit()
    db.refresh(config)
    return config
    
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

@app.post("/{slug}/barbeiros/", response_model=schemas.UsuarioResponse)
def criar_barbeiro(slug: str, usuario_logado_id: int, barbeiro: schemas.UsuarioCreate, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    # 1. Verifica se quem está criando é realmente o administrador desta barbearia
    admin = db.query(models.Usuario).filter(models.Usuario.id == usuario_logado_id, models.Usuario.barbearia_id == barbearia.id).first()
    if not admin or admin.tipo != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas o administrador pode adicionar equipe.")
    
    # 2. Cria o barbeiro e vincula automaticamente à mesma barbearia
    db_usuario = models.Usuario(
        nome=barbeiro.nome, 
        email=barbeiro.email, 
        senha_hash=barbeiro.senha, 
        tipo="barbeiro", 
        telefone=barbeiro.telefone,
        barbearia_id=barbearia.id
    )
    db.add(db_usuario)
    try:
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado no sistema.")

@app.delete("/{slug}/barbeiros/{barbeiro_id}")
def deletar_barbeiro(slug: str, barbeiro_id: int, usuario_logado_id: int, db: Session = Depends(get_db), barbearia: models.Barbearia = Depends(obter_barbearia)):
    admin = db.query(models.Usuario).filter(models.Usuario.id == usuario_logado_id, models.Usuario.barbearia_id == barbearia.id).first()
    if not admin or admin.tipo != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado.")
        
    barbeiro = db.query(models.Usuario).filter(models.Usuario.id == barbeiro_id, models.Usuario.barbearia_id == barbearia.id, models.Usuario.tipo == "barbeiro").first()
    if not barbeiro:
        raise HTTPException(status_code=404, detail="Barbeiro não encontrado.")
        
    db.delete(barbeiro)
    db.commit()
    return {"message": "Barbeiro removido com sucesso."}