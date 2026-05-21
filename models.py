from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base



class Obra(Base):
    __tablename__ = "obras"

    id = Column(Integer, primary_key=True)
    titulo_obra = Column(String(200), nullable=False)
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria = Column(String(120), nullable=True)
    ano = Column(Integer, nullable=True)
    editora = Column(String(120), nullable=True)
    
    capitulos = relationship("Capitulo", back_populates="obra")
    autor = relationship("Usuario", back_populates="obras")
    pdf_urls = relationship("PdfUrl", back_populates="obra")

    def to_dict(self):
        autor_nome = self.autor.nome if self.autor else None
        return {"id": self.id, "titulo": self.titulo_obra, "autor": autor_nome, "autor_id": self.autor_id}

    def __repr__(self):
        return f"<Obra {self.id} {self.titulo_obra!r}>"


class Capitulo(Base):
    __tablename__ = "capitulos"
    id = Column(Integer, primary_key=True)
    titulo_capitulo = Column(String(200), nullable=False)
    numero_capitulo = Column(Integer, nullable=True)
    obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)

    obra = relationship("Obra", back_populates="capitulos")

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo_capitulo,
            "numero": self.numero_capitulo,
            "obra_id": self.obra_id,
        }

    def __repr__(self): # Changed to use titulo_capitulo for consistency
        return f"<Capitulo {self.id} {self.titulo_capitulo!r}>"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    senha = Column(String(120), nullable=True)
    obras = relationship("Obra", back_populates="autor")

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "email": self.email}

    def __repr__(self):
        return f"<Usuario {self.id} {self.nome!r}>"


class PdfUrl(Base):
    __tablename__ = "pdf_urls"

    id = Column(Integer, primary_key=True)
    url = Column(String(200), nullable=False)
    obra_id = Column(Integer, ForeignKey("obras.id"), nullable=False)
    capitulo_id = Column(Integer, ForeignKey("capitulos.id"), nullable=True)

    obra = relationship("Obra", back_populates="pdf_urls")
    capitulo = relationship("Capitulo")

    def to_dict(self):
        return {"id": self.id, "url": self.url, "obra_id": self.obra_id, "capitulo_id": self.capitulo_id}

    def __repr__(self):
        return f"<pdf_url {self.id} {self.url!r}>"

# class Professor(Base):
#     __tablename__ = "professores"

#     id = Column(Integer, primary_key=True)
#     nome = Column(String(120), nullable=False)
#     email = Column(String(120), unique=True, nullable=True)

#     turmas = relationship("Turma", back_populates="professor")

#     def to_dict(self):
#         return {"id": self.id, "nome": self.nome, "email": self.email}

#     def __repr__(self):
#         return f"<Professor {self.id} {self.nome!r}>"

# class Turma(Base):
#     __tablename__ = "turmas"

#     id = Column(Integer, primary_key=True)
#     nome = Column(String(120), nullable=False)
#     codigo = Column(String(40), unique=True, nullable=False)
#     professor_id = Column(Integer, ForeignKey("professores.id"), nullable=False)

#     professor = relationship("Professor", back_populates="turmas")
#     alunos = relationship("Aluno", back_populates="turma")

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "nome": self.nome,
#             "codigo": self.codigo,
#             "professor_id": self.professor_id,
#         }

#     def __repr__(self):
#         return f"<Turma {self.id} {self.codigo!r}>"


# class Aluno(Base):
#     __tablename__ = "alunos"

#     id = Column(Integer, primary_key=True)
#     nome = Column(String(120), nullable=False)
#     email = Column(String(120), unique=True, nullable=True)
#     turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)

#     turma = relationship("Turma", back_populates="alunos")

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "nome": self.nome,
#             "email": self.email,
#             "turma_id": self.turma_id,
#         }

#     def __repr__(self):
#         return f"<Aluno {self.id} {self.nome!r}>"