# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    tipo = Column(String) 
    telefone = Column(String, nullable=True) 

    agendamentos_como_cliente = relationship("Agendamento", foreign_keys='Agendamento.cliente_id', back_populates="cliente")
    agendamentos_como_barbeiro = relationship("Agendamento", foreign_keys='Agendamento.barbeiro_id', back_populates="barbeiro")


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    barbeiro_id = Column(Integer, ForeignKey("usuarios.id"))
    servico = Column(String) 
    data_hora = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="Pendente") 
    preco = Column(Float, default=0.0) # <--- NOVO CAMPO FINANCEIRO
    google_event_id = Column(String, nullable=True) # ADICIONE ESTA LINHA
    cliente = relationship("Usuario", foreign_keys=[cliente_id], back_populates="agendamentos_como_cliente")
    barbeiro = relationship("Usuario", foreign_keys=[barbeiro_id], back_populates="agendamentos_como_barbeiro")
    cliente = relationship("Usuario", foreign_keys=[cliente_id])
    barbeiro = relationship("Usuario", foreign_keys=[barbeiro_id])
    @property
    def cliente_nome(self):
        return self.cliente.nome if self.cliente else "Desconhecido"

    @property
    def barbeiro_nome(self):
        return self.barbeiro.nome if self.barbeiro else "Desconhecido"
    
class GoogleToken(Base):
    __tablename__ = "google_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    access_token = Column(String)
    refresh_token = Column(String)
    token_expiry = Column(DateTime)