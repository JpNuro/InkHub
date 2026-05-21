from database import engine
from sqlalchemy import text

# Adicionar coluna capitulo_id à tabela pdf_urls
# SQLite não suporta ADD FOREIGN KEY em ALTER TABLE, apenas a coluna
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE pdf_urls ADD COLUMN capitulo_id INTEGER"))
        conn.commit()
        print("Coluna capitulo_id adicionada com sucesso à tabela pdf_urls")
    except Exception as e:
        print(f"Erro ao adicionar coluna (pode já existir): {e}")
        conn.rollback()
