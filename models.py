"""
Modelos de banco de dados usando SQLAlchemy ORM.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Usuario(Base):
  __tablename__ = "usuarios"

  id = Column(Integer, primary_key=True)
  nome = Column(String(200), nullable=False)
  email = Column(String(200), nullable=False)
  senha = Column(String(200), nullable=True)

  obras = relationship("Obra", back_populates="autor")

  def to_dict(self):
    return {
      "id": self.id,
      "nome": self.nome,
      "email": self.email,
    }

  def __repr__(self):
    return f"<Usuario {self.id} {self.nome!r}>"


class Obra(Base):
  __tablename__ = "obras"

  id = Column(Integer, primary_key=True)
  titulo_obra = Column(String(200), nullable=False)
  autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
  categoria = Column(String(100), nullable=True)
  ano = Column(Integer, nullable=True)
  editora = Column(String(200), nullable=True)

  capitulos = relationship("Capitulo", back_populates="obra")
  autor = relationship("Usuario", back_populates="obras")
  pdf_urls = relationship("PdfUrl", back_populates="obra")

  def to_dict(self):
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


class Capitulo(Base):
  __tablename__ = "capitulos"

  id = Column(Integer, primary_key=True)
  titulo_capitulo = Column(String(200), nullable=False)
  numero_capitulo = Column(Integer, nullable=True)
  obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)

  obra = relationship("Obra", back_populates="capitulos")
  pdf_urls = relationship("PdfUrl", back_populates="capitulo")

  def to_dict(self):
    return {
      "id": self.id,
      "titulo": self.titulo_capitulo,
      "numero": self.numero_capitulo,
      "obra_id": self.obra_id,
    }

  def __repr__(self):
    return f"<Capitulo {self.id} {self.titulo_capitulo!r}>"


class PdfUrl(Base):
  __tablename__ = "pdf_urls"

  id = Column(Integer, primary_key=True)
  url = Column(String(500), nullable=False)
  obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)
  capitulo_id = Column(Integer, ForeignKey("capitulos.id"), nullable=True)

  obra = relationship("Obra", back_populates="pdf_urls")
  capitulo = relationship("Capitulo", back_populates="pdf_urls")

  def to_dict(self):
    return {
      "id": self.id,
      "url": self.url,
      "obra_id": self.obra_id,
      "capitulo_id": self.capitulo_id,
    }

  def __repr__(self):
    return f"<PdfUrl {self.id} obra={self.obra_id}>"