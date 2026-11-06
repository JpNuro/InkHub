# Bibliotecas para criar a conexão SQLite e a base declarativa dos modelos.
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# O caminho do banco é compartilhado com a configuração principal do projeto.
from config import INSTANCE_DIR

# Cria o mecanismo de conexão com o arquivo SQLite local.
engine = create_engine(f"sqlite:///{INSTANCE_DIR}/app.db", echo=False)

# Cada chamada cria uma sessão independente, sem commit automático.
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base usada pelas classes ORM para registrar tabelas e metadados.
Base = declarative_base()


def criar_tabelas():
    """Cria tabelas ausentes sem remover as existentes."""
    Base.metadata.create_all(bind=engine)
