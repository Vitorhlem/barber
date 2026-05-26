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
    cliente: Optional[UsuarioBase] = None
    barbeiro: Optional[UsuarioBase] = None

    class Config:
        from_attributes = True

# --- BLOQUEIOS DE HORÁRIO ---
class BloqueioBase(BaseModel):
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
    intervalo_minutos: int
    horarios_json: str
    loja_aberta: bool = True

class ConfiguracaoBarbeiroResponse(ConfiguracaoBarbeiroBase):
    id: int
    barbeiro_id: int
    class Config:
        from_attributes = True

class ProdutoBase(BaseModel):
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

class ConfiguracaoSistemaBase(BaseModel):
    nome_barbearia: str
    logo_url: Optional[str] = None

class ConfiguracaoSistemaResponse(ConfiguracaoSistemaBase):
    id: int
    class Config:
        from_attributes = True

class FolgaPontualBase(BaseModel):
    barbeiro_id: int
    data: str
    motivo: Optional[str] = None

class FolgaPontualCreate(FolgaPontualBase):
    pass

class FolgaPontualResponse(FolgaPontualBase):
    id: int
    class Config:
        from_attributes = True

class ServicoBase(BaseModel):
    nome: str
    preco: float

class ServicoCreate(ServicoBase):
    pass

class ServicoResponse(ServicoBase):
    id: int
    class Config:
        from_attributes = True