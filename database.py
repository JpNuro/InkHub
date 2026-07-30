"""
Configuração do banco de dados SQLite usando SQLAlchemy.
Define a base declarativa e a fábrica de sessões.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import INSTANCE_DIR

# ── Configuração do Banco de Dados ───────────────────────────────────────────────
# Cria o engine do SQLite (arquivo local)
engine = create_engine("sqlite:///inkhub.db", echo=False)

# Cria a fábrica de sessões para gerenciar conexões com o banco
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base declarativa para os modelos ORM
Base = declarative_base()


# ── Função para criar as tabelas ─────────────────────────────────────────────────
def criar_tabelas():
  """Cria todas as tabelas no banco de dados se não existirem."""
  Base.metadata.create_all(bind=engine)
