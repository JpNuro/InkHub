"""
Modelos de banco de dados usando SQLAlchemy ORM.
Cada classe representa uma tabela no banco SQLite.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


# ── Modelo de Usuário ───────────────────────────────────────────────────────────
class Usuario(Base):
  """Tabela de usuários do sistema."""
  __tablename__ = "usuarios"

  id = Column(Integer, primary_key=True)           # ID único do usuário
  nome = Column(String(200), nullable=False)       # Nome completo do usuário
  email = Column(String(200), nullable=False)      # E-mail único do usuário
  senha = Column(String(200), nullable=True)       # Senha hasheada (pode ser None para compatibilidade)

  obras = relationship("Obra", back_populates="autor")

  def to_dict(self):
    """Converte o objeto para dicionário para serialização JSON."""
    return {
      "id": self.id,
      "nome": self.nome,
      "email": self.email,
    }

  def __repr__(self):
    return f"<Usuario {self.id} {self.nome!r}>"


# ── Modelo de Obra ─────────────────────────────────────────────────────────────
class Obra(Base):
  """Tabela de obras (mangás, quadrinhos, etc)."""
  __tablename__ = "obras"

  id = Column(Integer, primary_key=True)           # ID único da obra
  titulo_obra = Column(String(200), nullable=False)  # Título da obra
  autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)  # ID do autor (usuário)
  categoria = Column(String(100), nullable=True)   # Categoria (Shonen, Seinen, etc)
  ano = Column(Integer, nullable=True)              # Ano de lançamento
  editora = Column(String(200), nullable=True)     # Editora da obra

  # Relacionamento com capítulos (uma obra tem muitos capítulos)
  capitulos = relationship("Capitulo", back_populates="obra")
  # Relacionamento com usuário autor (uma obra pertence a um usuário)
  autor = relationship("Usuario", back_populates="obras")
  pdf_urls = relationship("PdfUrl", back_populates="obra")

  def to_dict(self):
    """Converte o objeto para dicionário para serialização JSON."""
    return {
      "id": self.id,
      "titulo": self.titulo_obra,
      "autor_id": self.autor_id,
      "autor": self.autor.nome if self.autor else None,
      "categoria": self.categoria,
      "ano": self.ano,
      "editora": self.editora,
    }

  def __repr__(self):
    return f"<Obra {self.id} {self.titulo_obra!r}>"


# ── Modelo de Capítulo ─────────────────────────────────────────────────────────
class Capitulo(Base):
  """Tabela de capítulos das obras."""
  __tablename__ = "capitulos"

  id = Column(Integer, primary_key=True)           # ID único do capítulo
  titulo_capitulo = Column(String(200), nullable=False)  # Título do capítulo
  numero_capitulo = Column(Integer, nullable=True)  # Número do capítulo (auto-incrementado)
  obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)  # ID da obra

  # Relacionamento com obra (um capítulo pertence a uma obra)
  obra = relationship("Obra", back_populates="capitulos")
  pdf_urls = relationship("PdfUrl", back_populates="capitulo")

  def to_dict(self):
    """Converte o objeto para dicionário para serialização JSON."""
    return {
      "id": self.id,
      "titulo": self.titulo_capitulo,
      "numero": self.numero_capitulo,
      "obra_id": self.obra_id,
    }

  def __repr__(self):
    return f"<Capitulo {self.id} {self.titulo_capitulo!r}>"


# ── Modelo de PDF URL ─────────────────────────────────────────────────────────
class PdfUrl(Base):
  """Tabela de URLs de PDFs armazenados no Cloudinary."""
  __tablename__ = "pdf_urls"

  id = Column(Integer, primary_key=True)           # ID único do registro
  url = Column(String(500), nullable=False)        # URL pública do PDF no Cloudinary
  obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)  # ID da obra
  capitulo_id = Column(Integer, ForeignKey("capitulos.id"), nullable=True)  # ID do capítulo (opcional)

  # Relacionamentos
  obra = relationship("Obra", back_populates="pdf_urls")
  capitulo = relationship("Capitulo", back_populates="pdf_urls")

  def to_dict(self):
    """Converte o objeto para dicionário para serialização JSON."""
    return {
      "id": self.id,
      "url": self.url,
      "obra_id": self.obra_id,
      "capitulo_id": self.capitulo_id,
    }

  def __repr__(self):
    return f"<PdfUrl {self.id} obra={self.obra_id}>"