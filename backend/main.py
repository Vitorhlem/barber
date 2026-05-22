from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, List
from sqlalchemy.exc import IntegrityError
import models
import schemas
from database import engine, get_db

# Criação das tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PetCare Plus API")

# Gerenciador de WebSockets
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

# Configuração de CORS
origens_permitidas = [
    "http://localhost:5173",  # Porta do Vue
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "https://petcarev.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origens_permitidas,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROTAS DE USUÁRIOS ---

@app.post("/usuarios/", response_model=schemas.UsuarioResponse)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = models.Usuario(
        nome=usuario.nome, 
        email=usuario.email, 
        senha_hash=usuario.senha, 
        tipo=usuario.tipo, 
        crmv=usuario.crmv
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@app.post("/login/", response_model=schemas.UsuarioResponse)
def login(usuario: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if not db_usuario or db_usuario.senha_hash != usuario.senha:
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    return db_usuario

# --- ROTAS DE PETS ---

@app.post("/usuarios/{tutor_id}/pets/", response_model=schemas.PetResponse)
def criar_pet_para_tutor(tutor_id: int, pet: schemas.PetCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id == tutor_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    
    db_pet = models.Pet(**pet.model_dump(), tutor_id=tutor_id)
    db.add(db_pet)
    try:
        db.commit()
        db.refresh(db_pet)
        return db_pet
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro de integridade no banco de dados.")

@app.get("/usuarios/{tutor_id}/pets/", response_model=List[schemas.PetResponse])
def listar_pets_do_tutor(tutor_id: int, db: Session = Depends(get_db)):
    return db.query(models.Pet).filter(models.Pet.tutor_id == tutor_id).all()

@app.get("/pets/", response_model=List[schemas.PetResponse])
def listar_todos_os_pets(db: Session = Depends(get_db)):
    return db.query(models.Pet).all()

@app.get("/pets/{pet_id}", response_model=schemas.PetResponse)
def ler_pet(pet_id: int, db: Session = Depends(get_db)):
    db_pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not db_pet:
        raise HTTPException(status_code=404, detail="Pet não encontrado")
    return db_pet

@app.put("/pets/{pet_id}", response_model=schemas.PetResponse)
def atualizar_pet(pet_id: int, pet: schemas.PetCreate, db: Session = Depends(get_db)):
    db_pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not db_pet:
        raise HTTPException(status_code=404, detail="Pet não encontrado")
    for key, value in pet.model_dump().items():
        setattr(db_pet, key, value)
    db.commit()
    db.refresh(db_pet)
    return db_pet

@app.delete("/pets/{pet_id}")
def deletar_pet(pet_id: int, db: Session = Depends(get_db)):
    db_pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not db_pet:
        raise HTTPException(status_code=404, detail="Pet não encontrado")
    db.query(models.Registro).filter(models.Registro.pet_id == pet_id).delete()
    db.delete(db_pet)
    db.commit()
    return {"message": "Pet excluído com sucesso"}

# --- ROTAS DE REGISTROS ---

@app.post("/pets/{pet_id}/registros/", response_model=schemas.RegistroResponse)
async def criar_registro_para_pet(pet_id: int, registro: schemas.RegistroCreate, db: Session = Depends(get_db)):
    db_pet = db.query(models.Pet).filter(models.Pet.id == pet_id).first()
    if not db_pet:
        raise HTTPException(status_code=404, detail="Pet não encontrado")
    
    db_registro = models.Registro(**registro.model_dump(), pet_id=pet_id)
    db.add(db_registro)
    db.commit()
    db.refresh(db_registro)
    
    # Notificação via WebSocket
    mensagem = f"Atualizacao no pet {db_pet.nome}: {registro.nome}"
    await manager.send_personal_message(mensagem, db_pet.tutor_id)
    
    return db_registro

@app.put("/registros/{registro_id}", response_model=schemas.RegistroResponse)
def atualizar_registro(registro_id: int, registro: schemas.RegistroCreate, db: Session = Depends(get_db)):
    db_registro = db.query(models.Registro).filter(models.Registro.id == registro_id).first()
    if not db_registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    for key, value in registro.model_dump().items():
        setattr(db_registro, key, value)
    db.commit()
    db.refresh(db_registro)
    return db_registro

@app.delete("/registros/{registro_id}")
def deletar_registro(registro_id: int, db: Session = Depends(get_db)):
    db_registro = db.query(models.Registro).filter(models.Registro.id == registro_id).first()
    if not db_registro:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    db.delete(db_registro)
    db.commit()
    return {"message": "Registro excluído com sucesso"}

# --- WEBSOCKET ---

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)