from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- USUÁRIOS ---
class UsuarioBase(BaseModel):
    nome: str
    email: str
    tipo: str
    telefone: Optional[str] = None
    barbearia_id: Optional[int] = None # Adicionado

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
    barbearia_id: int # Adicionado para garantir o isolamento
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
    cliente: Optional[UsuarioBase] = None
    barbeiro: Optional[UsuarioBase] = None

    class Config:
        from_attributes = True

# --- BLOQUEIOS DE HORÁRIO ---
class BloqueioBase(BaseModel):
    barbearia_id: int
    barbeiro_id: int
    inicio: datetime
    fim: datetime
    motivo: str

class BloqueioCreate(BloqueioBase):
    pass

class BloqueioResponse(BloqueioBase):
    id: int
    class Config:
        from_attributes = True

# --- CONFIGURAÇÕES DO BARBEIRO ---
class ConfiguracaoBarbeiroBase(BaseModel):
    barbearia_id: int
    intervalo_minutos: int
    horarios_json: str
    loja_aberta: bool = True

class ConfiguracaoBarbeiroResponse(ConfiguracaoBarbeiroBase):
    id: int
    barbeiro_id: int
    class Config:
        from_attributes = True

# --- PRODUTOS ---
class ProdutoBase(BaseModel):
    barbearia_id: int
    nome: str
    descricao: Optional[str] = None
    preco: float
    categoria: str
    imagem_url: Optional[str] = None

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoResponse(ProdutoBase):
    id: int
    class Config:
        from_attributes = True

# --- SERVIÇOS ---
class ServicoBase(BaseModel):
    barbearia_id: int
    nome: str
    preco: float

class ServicoCreate(ServicoBase):
    pass

class ServicoResponse(ServicoBase):
    id: int
    class Config:
        from_attributes = True

# --- FOLGAS ---
class FolgaPontualBase(BaseModel):
    barbearia_id: int
    barbeiro_id: int
    data: str
    motivo: Optional[str] = None

class FolgaPontualCreate(FolgaPontualBase):
    pass

class FolgaPontualResponse(FolgaPontualBase):
    id: int
    class Config:
        from_attributes = True

