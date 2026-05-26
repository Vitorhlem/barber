# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
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
    preco = Column(Float, default=0.0)
    google_event_id = Column(String, nullable=True)
    
    cliente = relationship("Usuario", foreign_keys=[cliente_id], back_populates="agendamentos_como_cliente")
    barbeiro = relationship("Usuario", foreign_keys=[barbeiro_id], back_populates="agendamentos_como_barbeiro")
    
    @property
    def cliente_nome(self):
        return self.cliente.nome if self.cliente else "Desconhecido"

    @property
    def barbeiro_nome(self):
        return self.barbeiro.nome if self.barbeiro else "Desconhecido"

class BloqueioHorario(Base):
    __tablename__ = "bloqueios_horario"
    
    id = Column(Integer, primary_key=True, index=True)
    barbeiro_id = Column(Integer, ForeignKey("usuarios.id"))
    inicio = Column(DateTime)
    fim = Column(DateTime)
    motivo = Column(String, default="Pausa")
    
    barbeiro = relationship("Usuario", foreign_keys=[barbeiro_id])

class ConfiguracaoBarbeiro(Base):
    __tablename__ = "configuracoes_barbeiro"
    
    id = Column(Integer, primary_key=True, index=True)
    barbeiro_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    intervalo_minutos = Column(Integer, default=30)
    horarios_json = Column(String, default='[]')
    loja_aberta = Column(Boolean, default=True) 

class GoogleToken(Base):
    __tablename__ = "google_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"))
    access_token = Column(String)
    refresh_token = Column(String)
    token_expiry = Column(DateTime)

class Produto(Base):
    __tablename__ = "produtos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    descricao = Column(String, nullable=True)
    preco = Column(Float, default=0.0)
    categoria = Column(String, index=True)
    imagem_url = Column(String, nullable=True)

class ConfiguracaoSistema(Base):
    __tablename__ = "configuracao_sistema"
    
    id = Column(Integer, primary_key=True, index=True)
    nome_barbearia = Column(String, default="BarberBase")
    logo_url = Column(String, nullable=True)

class FolgaPontual(Base):
    __tablename__ = "folgas_pontuais"
    
    id = Column(Integer, primary_key=True, index=True)
    barbeiro_id = Column(Integer, ForeignKey("usuarios.id"))
    data = Column(String, index=True)  # Armazena no formato 'YYYY-MM-DD'
    motivo = Column(String, nullable=True)
    
    barbeiro = relationship("Usuario", foreign_keys=[barbeiro_id])  

class Servico(Base):
    __tablename__ = "servicos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    preco = Column(Float, default=0.0)