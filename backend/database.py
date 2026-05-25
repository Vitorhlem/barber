# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# String de conexão para rodar local no pgAdmin (Substitua 'postgres' e 'suasenha' pelos seus dados locais, e crie o banco 'barberbase')
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Admin123@localhost:5432/barber"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()