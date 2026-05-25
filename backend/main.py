import os
import uuid
import base64
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
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

app = FastAPI(title="BarberBase API")

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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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

# --- ROTAS DE AUTENTICAÇÃO ---
@app.get("/auth/google/login")
async def login_google(user_id: int):
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode().replace("=", "")
    state_id = str(uuid.uuid4())
    
    auth_state_store[state_id] = {"user_id": user_id, "code_verifier": code_verifier}
    
    flow = Flow.from_client_secrets_file("client_secret.json", scopes=['https://www.googleapis.com/auth/calendar'], redirect_uri='http://localhost:8000/auth/callback')
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', state=state_id, code_challenge=code_challenge, code_challenge_method='S256')
    return {"url": auth_url}

@app.get("/auth/callback")
async def oauth2_callback(code: str, state: str, db: Session = Depends(get_db)):
    data = auth_state_store.get(state)
    if not data:
        raise HTTPException(status_code=400, detail="Pedido inválido.")
    
    user_id = data["user_id"]
    code_verifier = data["code_verifier"]
    del auth_state_store[state]

    flow = Flow.from_client_secrets_file("client_secret.json", scopes=['https://www.googleapis.com/auth/calendar'], redirect_uri='http://localhost:8000/auth/callback')
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
    
    return RedirectResponse(url="http://localhost:5173/dashboard")

# --- ROTAS DE USUÁRIOS E AGENDAMENTOS ---
@app.post("/usuarios/", response_model=schemas.UsuarioResponse)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = models.Usuario(nome=usuario.nome, email=usuario.email, senha_hash=usuario.senha, tipo=usuario.tipo, telefone=usuario.telefone)
    db.add(db_usuario)
    try:
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

@app.post("/login/", response_model=schemas.UsuarioResponse)
def login(usuario: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if not db_usuario or db_usuario.senha_hash != usuario.senha:
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    return db_usuario

@app.post("/usuarios/{cliente_id}/agendamentos", response_model=schemas.AgendamentoResponse)
@app.post("/usuarios/{cliente_id}/agendamentos/", response_model=schemas.AgendamentoResponse)
async def criar_agendamento(cliente_id: int, agendamento: schemas.AgendamentoCreate, db: Session = Depends(get_db)):
    db_agendamento = models.Agendamento(**agendamento.model_dump(), cliente_id=cliente_id)
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

@app.get("/agendamentos/barbeiro/{barbeiro_id}", response_model=List[schemas.AgendamentoResponse])
@app.get("/agendamentos/barbeiro/{barbeiro_id}/", response_model=List[schemas.AgendamentoResponse])
def listar_agendamentos(barbeiro_id: int, db: Session = Depends(get_db)):
    return db.query(models.Agendamento).options(
        joinedload(models.Agendamento.cliente),
        joinedload(models.Agendamento.barbeiro)
    ).filter(models.Agendamento.barbeiro_id == barbeiro_id).all()

@app.put("/agendamentos/{agendamento_id}", response_model=schemas.AgendamentoResponse)
async def atualizar(agendamento_id: int, agendamento_update: schemas.AgendamentoUpdate, db: Session = Depends(get_db)):
    db_agendamento = db.query(models.Agendamento).filter(models.Agendamento.id == agendamento_id).first()
    db_agendamento.status = agendamento_update.status
    db.commit()
    db.refresh(db_agendamento)
    
    await manager.broadcast_update(db_agendamento.cliente_id, "UPDATE_AGENDAMENTOS")
    await manager.broadcast_update(db_agendamento.barbeiro_id, "UPDATE_AGENDAMENTOS")
    
    return db_agendamento

@app.delete("/agendamentos/{agendamento_id}")
async def deletar_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    db_agendamento = db.query(models.Agendamento).filter(models.Agendamento.id == agendamento_id).first()
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

@app.get("/usuarios/{cliente_id}/agendamentos")
def listar_agendamentos_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return db.query(models.Agendamento).options(
        joinedload(models.Agendamento.cliente),
        joinedload(models.Agendamento.barbeiro)
    ).filter(models.Agendamento.cliente_id == cliente_id).all()

@app.get("/agendamentos/{agendamento_id}", response_model=schemas.AgendamentoResponse)
def buscar_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = db.query(models.Agendamento).options(
        joinedload(models.Agendamento.cliente),
        joinedload(models.Agendamento.barbeiro)
    ).filter(models.Agendamento.id == agendamento_id).first()
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return agendamento

@app.get("/barbeiros/", response_model=List[schemas.UsuarioResponse])
def listar_barbeiros(db: Session = Depends(get_db)):
    return db.query(models.Usuario).filter(models.Usuario.tipo == "barbeiro").all()

# --- BLOQUEIOS DE HORÁRIOS ---
@app.post("/bloqueios/", response_model=schemas.BloqueioResponse)
async def criar_bloqueio(bloqueio: schemas.BloqueioCreate, db: Session = Depends(get_db)):
    db_bloqueio = models.BloqueioHorario(**bloqueio.model_dump())
    db.add(db_bloqueio)
    db.commit()
    db.refresh(db_bloqueio)
    await manager.broadcast_update(bloqueio.barbeiro_id, "UPDATE_BLOQUEIOS")
    return db_bloqueio

@app.get("/bloqueios/barbeiro/{barbeiro_id}", response_model=List[schemas.BloqueioResponse])
def listar_bloqueios(barbeiro_id: int, db: Session = Depends(get_db)):
    return db.query(models.BloqueioHorario).filter(models.BloqueioHorario.barbeiro_id == barbeiro_id).all()

@app.delete("/bloqueios/{bloqueio_id}")
async def deletar_bloqueio(bloqueio_id: int, db: Session = Depends(get_db)):
    db_bloqueio = db.query(models.BloqueioHorario).filter(models.BloqueioHorario.id == bloqueio_id).first()
    if not db_bloqueio:
        raise HTTPException(status_code=404, detail="Bloqueio não encontrado")
    
    barbeiro_id = db_bloqueio.barbeiro_id
    db.delete(db_bloqueio)
    db.commit()
    
    await manager.broadcast_update(barbeiro_id, "UPDATE_BLOQUEIOS")
    return {"message": "Bloqueio removido"}

@app.get("/produtos/", response_model=List[schemas.ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(models.Produto).all()

@app.post("/produtos/", response_model=schemas.ProdutoResponse)
def criar_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = models.Produto(**produto.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

@app.delete("/produtos/{produto_id}")
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    db_produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(db_produto)
    db.commit()
    return {"message": "Produto removido"}

# --- ROTAS DE CONFIGURAÇÃO DE HORÁRIO DO BARBEIRO ---
@app.get("/configuracao/{barbeiro_id}", response_model=schemas.ConfiguracaoBarbeiroResponse)
def obter_configuracao(barbeiro_id: int, db: Session = Depends(get_db)):
    config = db.query(models.ConfiguracaoBarbeiro).filter(models.ConfiguracaoBarbeiro.barbeiro_id == barbeiro_id).first()
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
            intervalo_minutos=30,
            horarios_json=json.dumps(default_horarios),
            loja_aberta=True
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

@app.put("/configuracao/{barbeiro_id}", response_model=schemas.ConfiguracaoBarbeiroResponse)
def atualizar_configuracao(barbeiro_id: int, config_update: schemas.ConfiguracaoBarbeiroBase, db: Session = Depends(get_db)):
    config = db.query(models.ConfiguracaoBarbeiro).filter(models.ConfiguracaoBarbeiro.barbeiro_id == barbeiro_id).first()
    if not config:
        config = models.ConfiguracaoBarbeiro(barbeiro_id=barbeiro_id)
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