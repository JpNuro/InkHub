"""
Modelos das tabelas do InkHub usando o ORM do SQLAlchemy.
"""

# Tipos de coluna, chaves estrangeiras e relações entre modelos.
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# Todas as classes abaixo herdam da base configurada para o banco SQLite.
from database import Base


class Usuario(Base):
  """Pessoa cadastrada que pode ser autora de obras."""

  # Nome físico da tabela no banco.
  __tablename__ = "usuarios"

  # Dados básicos de identificação e credenciais do usuário.
  id = Column(Integer, primary_key=True)
  nome = Column(String(200), nullable=False)
  email = Column(String(200), nullable=False)
  senha = Column(String(200), nullable=True)

  # Relação inversa: lista as obras associadas a este autor.
  obras = relationship("Obra", back_populates="autor")

  def to_dict(self):
    """Converte o usuário para o formato público usado nas respostas JSON."""
    return {
      "id": self.id,
      "nome": self.nome,
      "email": self.email,
    }

  def __repr__(self):
    """Representação curta útil em logs e depuração."""
    return f"<Usuario {self.id} {self.nome!r}>"


class Obra(Base):
  """Mangá ou outra obra cadastrada no catálogo."""

  __tablename__ = "obras"

  # Metadados da obra e referência obrigatória ao usuário autor.
  id = Column(Integer, primary_key=True)
  titulo_obra = Column(String(200), nullable=False)
  autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
  categoria = Column(String(100), nullable=True)
  ano = Column(Integer, nullable=True)
  editora = Column(String(200), nullable=True)

  # Relações que permitem navegar entre obra, autor, capítulos e PDFs.
  capitulos = relationship("Capitulo", back_populates="obra")
  autor = relationship("Usuario", back_populates="obras")
  pdf_urls = relationship("PdfUrl", back_populates="obra")

  def to_dict(self):
    """Serializa metadados da obra, incluindo o nome do autor."""
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
    """Representação curta útil em logs e depuração."""
    return f"<Obra {self.id} {self.titulo_obra!r}>"


class Capitulo(Base):
  """Capítulo pertencente a uma obra do catálogo."""

  __tablename__ = "capitulos"

  # Título, ordem do capítulo e chave estrangeira para sua obra.
  id = Column(Integer, primary_key=True)
  titulo_capitulo = Column(String(200), nullable=False)
  numero_capitulo = Column(Integer, nullable=True)
  obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)

  # A relação permite acessar a obra e os PDFs associados ao capítulo.
  obra = relationship("Obra", back_populates="capitulos")
  pdf_urls = relationship("PdfUrl", back_populates="capitulo")

  def to_dict(self):
    """Converte o capítulo para o formato usado pela API."""
    return {
      "id": self.id,
      "titulo": self.titulo_capitulo,
      "numero": self.numero_capitulo,
      "obra_id": self.obra_id,
    }

  def __repr__(self):
    """Representação curta útil em logs e depuração."""
    return f"<Capitulo {self.id} {self.titulo_capitulo!r}>"


class PdfUrl(Base):
  """URL pública de um PDF associado a uma obra ou capítulo."""

  __tablename__ = "pdf_urls"

  # A obra é obrigatória; o capítulo pode ficar vazio para PDF geral da obra.
  id = Column(Integer, primary_key=True)
  url = Column(String(500), nullable=False)
  obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)
  capitulo_id = Column(Integer, ForeignKey("capitulos.id"), nullable=True)

  # Relações ORM com a obra e, quando informado, com o capítulo.
  obra = relationship("Obra", back_populates="pdf_urls")
  capitulo = relationship("Capitulo", back_populates="pdf_urls")

  def to_dict(self):
    """Converte o registro do PDF para o formato de resposta da API."""
    return {
      "id": self.id,
      "url": self.url,
      "obra_id": self.obra_id,
      "capitulo_id": self.capitulo_id,
    }

  def __repr__(self):
    """Representação curta útil em logs e depuração."""
    return f"<PdfUrl {self.id} obra={self.obra_id}>"