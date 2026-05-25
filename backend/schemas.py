from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- USUÁRIOS ---
class UsuarioBase(BaseModel):
    nome: str
    email: str
    tipo: str
    telefone: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioLogin(BaseModel):
    email: str
    senha: str

class UsuarioResponse(UsuarioBase):
    id: int
    class Config:
        from_attributes = True

# --- AGENDAMENTOS ---
class AgendamentoBase(BaseModel):
    barbeiro_id: int
    servico: str
    data_hora: datetime
    preco: Optional[float] = 0.0

class AgendamentoCreate(AgendamentoBase):
    pass

class AgendamentoUpdate(BaseModel):
    status: str

class AgendamentoResponse(AgendamentoBase):
    id: int
    cliente_id: int
    status: str
    cliente_nome: str   
    barbeiro_nome: str  
    cliente: UsuarioBase # Adicione isto
    barbeiro: UsuarioBase # Adicione isto

    class Config:
        from_attributes = True