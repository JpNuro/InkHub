import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import INSTANCE_DIR

engine = create_engine(f"sqlite:///{INSTANCE_DIR}/app.db", echo=False)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def criar_tabelas():
    Base.metadata.create_all(bind=engine)
