"""
Script didático: DDL (create/drop tables) + DML (inserts) com sessão explícita.
Execute na raiz do projeto: python setup_database.py
"""

# from sqlalchemy import select

# from database import Base, SessionLocal, engine
# import models  # noqa: F401 — registra tabelas no metadata


# def populate_database():
#     print("Limpando e criando tabelas...")
#     Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)

#     session = SessionLocal()

#     try:
#         print("Inserindo professores...")
#         professores = [
#             models.Professor(nome="Maria Silva", email="maria@escola.example"),
#             models.Professor(nome="João Santos", email="joao.santos@escola.example"),
#         ]
#         session.add_all(professores)
#         session.flush()

#         print("Inserindo turmas...")
#         turmas = [
#             models.Turma(
#                 nome="Matemática A",
#                 codigo="MAT-2026-A",
#                 professor_id=professores[0].id,
#             ),
#             models.Turma(
#                 nome="Física B",
#                 codigo="FIS-2026-B",
#                 professor_id=professores[0].id,
#             ),
#             models.Turma(
#                 nome="Português A",
#                 codigo="PORT-2026-A",
#                 professor_id=professores[1].id,
#             ),
#         ]
#         session.add_all(turmas)
#         session.flush()

#         print("Inserindo alunos...")
#         alunos = [
#             models.Aluno(
#                 nome="Ana Costa",
#                 email="ana@escola.example",
#                 turma_id=turmas[0].id,
#             ),
#             models.Aluno(
#                 nome="Bruno Lima",
#                 email="bruno@escola.example",
#                 turma_id=turmas[0].id,
#             ),
#             models.Aluno(
#                 nome="Carla Dias",
#                 email="carla@escola.example",
#                 turma_id=turmas[1].id,
#             ),
#             models.Aluno(
#                 nome="Diego Rocha",
#                 email="diego@escola.example",
#                 turma_id=turmas[2].id,
#             ),
#         ]
#         session.add_all(alunos)

#         session.commit()
#         print("\nSucesso! Commit concluído.")

#         np = len(session.scalars(select(models.Professor)).all())
#         nt = len(session.scalars(select(models.Turma)).all())
#         na = len(session.scalars(select(models.Aluno)).all())
#         print(f"- Professores: {np}")
#         print(f"- Turmas: {nt}")
#         print(f"- Alunos: {na}")

#     except Exception as e:
#         print(f"Ocorreu um erro: {e}")
#         session.rollback()
#         raise
#     finally:
#         session.close()


# if __name__ == "__main__":
#     populate_database()



####
##      
## Minha parte ⬇️
##
####




# from sqlalchemy import select

# from database import Base, SessionLocal, engine
# import models


# def populate_database():
#     print("Limpando e criando tabelas...")
#     Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)

#     session = SessionLocal()

#     print("Tabelas criadas com sucesso!")
#     usuarios = [
#         models.Usuario(nome="Fujimoto", email="Fuji@gmail.com", senha="123"),
#         models.Usuario(nome="Masashi Kishimoto", email="Masamoto@gmail.com", senha="123"),
#     ]
#     session.add_all(usuarios)
#     session.flush()
#     session.commit()
#     print("Usuarios criados com sucesso!")

#     obras = [
#         models.Obra(titulo_obra="Vagabond", categoria="Seinen", autor_id=1),
#         models.Obra(titulo_obra="Bleach", categoria="Shonen", autor_id=2),
        
#     ]
#     session.add_all(obras)
#     session.flush()
#     session.commit()
#     print("Obras criadas com sucesso!")

#     caps = [
#         models.Capitulo(numero_capitulo=1, obra_id=1, titulo_capitulo="Primeiro Capítulo de Vagabond"),
#         models.Capitulo(numero_capitulo=2, obra_id=1, titulo_capitulo="Segundo Capítulo de Vagabond"),
#         models.Capitulo(numero_capitulo=1, obra_id=2, titulo_capitulo="Primeiro Capítulo de Bleach"),
#         models.Capitulo(numero_capitulo=2, obra_id=2, titulo_capitulo="Segundo Capítulo de Bleach"),
#     ]
#     session.add_all(caps)
#     session.flush()
#     session.commit()
#     print("Capítulos criados com sucesso!")

#     pdf_urls = [
#         models.PdfUrl(url="https://testejw267.com", obra_id=1),
        
#     ]
#     session.add_all(pdf_urls)
#     session.flush()
#     session.commit()
#     print("PDF URLs criadas com sucesso!")

#     usu = len(session.scalars(select(models.Usuario)).all())
#     print(f"Total de usuarios: {usu}")
#     oba = len(session.scalars(select(models.Obra)).all())
#     print(f"Total de obras: {oba}")
#     cap = len(session.scalars(select(models.Capitulo)).all())
#     print(f"Total de capítulos: {cap}")
#     pdf = len(session.scalars(select(models.PdfUrl)).all())
#     print(f"Total de PDF URLs: {pdf}")

# if __name__ == "__main__":
#     populate_database()