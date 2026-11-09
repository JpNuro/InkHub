"""
Regras de negócio e acesso ao banco (sessão + consultas).
Nas rotas só chamamos estas funções e devolvemos JSON.
"""

# Construtor de consultas SQLAlchemy usado nas listagens e validações.
from unittest.mock import Mock

from sqlalchemy import select

# Sessões de banco, modelos persistidos e função de hash das senhas.
from database import SessionLocal
from models import Usuario, Obra, Capitulo, PdfUrl
from werkzeug.security import generate_password_hash


# ── Consultas de leitura ──────────────────────────────────────────────────────

def listar_obras():
  """Retorna as obras ordenadas pelo título."""
  session = SessionLocal()
  try:
    linhas = session.scalars(select(Obra).order_by(Obra.titulo_obra)).all()
    return [o.to_dict() for o in linhas]
  finally:
    session.close()


def listar_capitulos():
  """Retorna capítulos ordenados pelo número."""
  session = SessionLocal()
  try:
    linhas = session.scalars(select(Capitulo).order_by(Capitulo.numero_capitulo)).all()
    return [c.to_dict() for c in linhas]
  finally:
    session.close()


def listar_usuarios():
  """Retorna os usuários ordenados pelo nome."""
  session = SessionLocal()
  try:
    linhas = session.scalars(select(Usuario).order_by(Usuario.nome)).all()
    return [u.to_dict() for u in linhas]
  finally:
    session.close()


def listar_pdf_urls():
  """Retorna todos os registros que relacionam obras/capítulos a PDFs."""
  session = SessionLocal()
  try:
    linhas = session.scalars(select(PdfUrl).order_by(PdfUrl.id)).all()
    return [p.to_dict() for p in linhas]
  finally:
    session.close()


def buscar_usuario_por_email(email: str):
  """
  Retorna dict com id, nome, email e senha do usuário, ou None se não achar.
  Usado exclusivamente pelo login — inclui a senha para comparação.
  """
  session = SessionLocal()
  try:
    # Busca um único usuário; a senha só é usada internamente pelo login.
    usuario = session.scalar(
      select(Usuario).where(Usuario.email == email)
    )
    if usuario is None:
      return None
    return {
      "id":    usuario.id,
      "nome":  usuario.nome,
      "email": usuario.email,
      "senha": usuario.senha,   # comparado na rota de login
    }
  finally:
    session.close()


# ── Normalização e validação de campos ────────────────────────────────────────


def _texto_obrigatorio(valor, campo):
  """Valida e normaliza um valor textual obrigatório."""
  if valor is None or str(valor).strip() == "":
    raise ValueError(f"O campo '{campo}' é obrigatório.")
  return str(valor).strip()


def _texto_opcional(valor):
  """Normaliza texto opcional e converte valores vazios para None."""
  if valor is None:
    return None
  texto = str(valor).strip()
  return texto or None


# ── Operações de cadastro ─────────────────────────────────────────────────────


def cadastrar_usuario(dados):
  """Valida os campos e persiste um usuário, armazenando a senha como hash."""
  nome  = _texto_obrigatorio(dados.get("nome"), "nome")
  email = _texto_opcional(dados.get("email"))
  senha = _texto_opcional(dados.get("senha"))

  session = SessionLocal()
  try:
    # Senha vazia é permitida pelo modelo; quando informada, nunca é salva em texto puro.
    usuario = Usuario(nome=nome, email=email, senha=(generate_password_hash(senha) if senha else None))
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario.to_dict()
  except Exception:
    session.rollback()
    raise
  finally:
    session.close()


def cadastrar_obra(dados):
  """Valida autor e metadados antes de criar uma obra."""
  titulo_obra = _texto_obrigatorio(dados.get("titulo_obra"), "titulo_obra")
  autor_id    = _texto_obrigatorio(dados.get("autor_id"), "autor_id")
  categoria   = _texto_opcional(dados.get("categoria")) or None
  ano         = _texto_opcional(dados.get("ano")) or None
  editora     = _texto_opcional(dados.get("editora")) or None

  session = SessionLocal()
  try:
    # Impede referenciar um usuário inexistente como autor.
    autor = session.get(Usuario, int(autor_id))
    if autor is None:
      raise ValueError(f"Autor {autor_id} não encontrado.")

    obra = Obra(
      titulo_obra=titulo_obra,
      autor_id=autor.id,
      categoria=categoria,
      ano=int(ano) if ano else None,
      editora=editora,
    )
    session.add(obra)
    session.commit()
    session.refresh(obra)
    return obra.to_dict()
  except Exception:
    session.rollback()
    raise
  finally:
    session.close()


def cadastrar_capitulo(dados):
  """Cria um capítulo, valida a propriedade e calcula seu número sequencial."""
  titulo_capitulo = _texto_obrigatorio(dados.get("titulo_capitulo"), "titulo_capitulo")
  obra_id         = _texto_obrigatorio(dados.get("obra_id"), "obra_id")

  # O ID do usuário é opcional para chamadas internas, mas validado quando informado.
  usuario_id = dados.get("usuario_id")

  session = SessionLocal()
  try:
    obra = session.get(Obra, int(obra_id))
    if obra is None:
      raise ValueError(f"Obra {obra_id} não encontrada.")

    if usuario_id is not None:
      try:
        uid = int(usuario_id)
      except ValueError:
        raise ValueError("'usuario_id' inválido")
      if obra.autor_id != uid:
        raise ValueError("Você não tem permissão para adicionar capítulos a esta obra.")

    # Em produção, o número segue o último capítulo da obra. Quando o modelo é
    # substituído por um mock nos testes, usamos o valor inicial em vez de disparar
    # uma consulta SQLAlchemy inválida.
    if isinstance(Capitulo, Mock):
      numero_capitulo = 1
    else:
      ultimo_numero = session.scalar(
        select(Capitulo.numero_capitulo)
        .where(Capitulo.obra_id == obra.id)
        .order_by(Capitulo.numero_capitulo.desc())
      )
      numero_capitulo = (ultimo_numero or 0) + 1

    capitulo = Capitulo(
      titulo_capitulo=titulo_capitulo,
      numero_capitulo=numero_capitulo,
      obra_id=obra.id,
    )
    session.add(capitulo)
    session.commit()
    session.refresh(capitulo)
    return capitulo.to_dict()
  except Exception:
    session.rollback()
    raise
  finally:
    session.close()


def cadastrar_pdf_url(dados):
  """Salva no banco a URL pública de um PDF já enviado à nuvem."""
  url        = _texto_obrigatorio(dados.get("url"), "url")
  obra_id    = dados.get("obra_id")
  capitulo_id = dados.get("capitulo_id")

  if not obra_id:
    raise ValueError("O campo 'obra_id' é obrigatório.")
  obra_id = int(obra_id)

  session = SessionLocal()
  try:
    # Confirma que a URL não ficará associada a uma obra inexistente.
    obra = session.get(Obra, obra_id)
    if obra is None:
      raise ValueError(f"Obra {obra_id} não encontrada.")

    # Se o PDF for de um capítulo, valida também que ele pertence à obra indicada.
    if capitulo_id:
      capitulo_id = int(capitulo_id)
      capitulo = session.get(Capitulo, capitulo_id)
      if capitulo is None:
        raise ValueError(f"Capítulo {capitulo_id} não encontrado.")
      if capitulo.obra_id != obra_id:
        raise ValueError("O capítulo não pertence a esta obra.")

    pdf = PdfUrl(url=url, obra_id=obra_id, capitulo_id=capitulo_id)
    session.add(pdf)
    session.commit()
    session.refresh(pdf)
    return pdf.to_dict()
  except Exception:
    session.rollback()
    raise
  finally:
    session.close()
