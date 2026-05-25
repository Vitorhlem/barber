import os
import uuid
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

# --- CONFIGURAÇÃO DE SEGURANÇA PARA LOCALHOST ---
# Isto resolve o erro de 'Missing code verifier' e permite o OAuth em HTTP
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

# --- IMPORTS DO PROJETO ---
import models
import schemas
from database import engine, get_db

# --- IMPORTS GOOGLE ---
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Criação das tabelas
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
    # O Google Auth precisa de um Client ID/Secret. Se o JSON não carregar, use variáveis
    creds = Credentials(
        token=token_entry.access_token,
        refresh_token=token_entry.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID", "SEU_ID_AQUI"), 
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", "SEU_SECRET_AQUI")
    )
    if creds.expired:
        creds.refresh(Request())
    return creds

def criar_evento_google(token_entry, agendamento, db): # <- Note o 'db' aqui também
    creds = get_valid_creds(token_entry)
    service = build('calendar', 'v3', credentials=creds)
    
    evento = {
        'summary': f'Atendimento: {agendamento.servico}',
        'description': f'Cliente: {agendamento.cliente_nome}',
        'start': {'dateTime': agendamento.data_hora.isoformat(), 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': (agendamento.data_hora + timedelta(minutes=30)).isoformat(), 'timeZone': 'America/Sao_Paulo'},
    }
    
    evento_criado = service.events().insert(calendarId='primary', body=evento).execute()
    
    # Agora o db está disponível aqui para salvar o ID
    agendamento.google_event_id = evento_criado.get('id')
    db.commit() # Salva o ID no banco
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

# Rota POST para agendar
@app.post("/usuarios/{cliente_id}/agendamentos", response_model=schemas.AgendamentoResponse)
@app.post("/usuarios/{cliente_id}/agendamentos/", response_model=schemas.AgendamentoResponse)
async def criar_agendamento(cliente_id: int, agendamento: schemas.AgendamentoCreate, db: Session = Depends(get_db)):
    # 1. Salvar no banco
    db_agendamento = models.Agendamento(**agendamento.model_dump(), cliente_id=cliente_id)
    db.add(db_agendamento)
    db.commit()
    db.refresh(db_agendamento)
    
    print(f"DEBUG: Agendamento salvo localmente ID: {db_agendamento.id}")
    
    # WebSocket
    await manager.send_personal_message(f"Novo agendamento: {db_agendamento.cliente_nome}", agendamento.barbeiro_id)
    
    # 2. Debug da Sincronização Google
    print(f"DEBUG: Tentando buscar token para barbeiro_id: {agendamento.barbeiro_id}")
    
    token_db = db.query(models.GoogleToken).filter(models.GoogleToken.user_id == agendamento.barbeiro_id).first()
    if token_db:
        try:
            # CORREÇÃO: Adicione o ', db' ao final da chamada
            criar_evento_google(token_db, db_agendamento, db)
            print("DEBUG: Evento criado com sucesso na API do Google!")
        except Exception as e:
            print(f"DEBUG CRÍTICO: Falha ao criar evento no Google: {e}")
    else:
        print(f"DEBUG: NENHUM token encontrado para o barbeiro_id {agendamento.barbeiro_id}. Verifique se ele fez login no Google.")
            
    return db_agendamento

# Rota GET para listar agendamentos do barbeiro
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
    return db_agendamento

@app.get("/barbeiros/", response_model=List[schemas.UsuarioResponse])
def listar_barbeiros(db: Session = Depends(get_db)):
    return db.query(models.Usuario).filter(models.Usuario.tipo == "barbeiro").all()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

@app.delete("/agendamentos/{agendamento_id}")
@app.delete("/agendamentos/{agendamento_id}/")
def deletar_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    db_agendamento = db.query(models.Agendamento).filter(models.Agendamento.id == agendamento_id).first()
    if not db_agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    # Excluir do Google (se existir ID)
    if db_agendamento.google_event_id:
        token_db = db.query(models.GoogleToken).filter(models.GoogleToken.user_id == db_agendamento.barbeiro_id).first()
        if token_db:
            try:
                creds = get_valid_creds(token_db)
                service = build('calendar', 'v3', credentials=creds)
                service.events().delete(calendarId='primary', eventId=db_agendamento.google_event_id).execute()
            except Exception as e:
                print(f"DEBUG: Erro ao deletar no Google: {e}")

    db.delete(db_agendamento)
    db.commit()
    return {"message": "Agendamento cancelado com sucesso"}

@app.get("/usuarios/{cliente_id}/agendamentos")
@app.get("/usuarios/{cliente_id}/agendamentos/")
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