"""
Regras de negócio e acesso ao banco (sessão + consultas).
Nas rotas só chamamos estas funções e devolvemos JSON.
"""

from sqlalchemy import select

from database import SessionLocal
from models import Usuario, Obra, Capitulo, PdfUrl


# ── Listagens ─────────────────────────────────────────────────────────────────

def listar_obras():
    session = SessionLocal()
    try:
        linhas = session.scalars(select(Obra).order_by(Obra.titulo_obra)).all()
        return [o.to_dict() for o in linhas]
    finally:
        session.close()


def listar_capitulos():
    session = SessionLocal()
    try:
        linhas = session.scalars(select(Capitulo).order_by(Capitulo.numero_capitulo)).all()
        return [c.to_dict() for c in linhas]
    finally:
        session.close()


def listar_usuarios():
    session = SessionLocal()
    try:
        linhas = session.scalars(select(Usuario).order_by(Usuario.nome)).all()
        return [u.to_dict() for u in linhas]
    finally:
        session.close()


def listar_pdf_urls():
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _texto_obrigatorio(valor, campo):
    if valor is None or str(valor).strip() == "":
        raise ValueError(f"O campo '{campo}' é obrigatório.")
    return str(valor).strip()


def _texto_opcional(valor):
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto or None


# ── Cadastros ─────────────────────────────────────────────────────────────────

def cadastrar_usuario(dados):
    nome  = _texto_obrigatorio(dados.get("nome"), "nome")
    email = _texto_opcional(dados.get("email"))

    session = SessionLocal()
    try:
        usuario = Usuario(nome=nome, email=email)
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
    titulo_obra = _texto_obrigatorio(dados.get("titulo_obra"), "titulo_obra")
    autor_id    = _texto_obrigatorio(dados.get("autor_id"), "autor_id")
    categoria   = _texto_opcional(dados.get("categoria")) or None
    ano         = _texto_opcional(dados.get("ano")) or None
    editora     = _texto_opcional(dados.get("editora")) or None

    session = SessionLocal()
    try:
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
    titulo_capitulo = _texto_obrigatorio(dados.get("titulo_capitulo"), "titulo_capitulo")
    numero_capitulo = _texto_obrigatorio(dados.get("numero_capitulo"), "numero_capitulo")
    obra_id         = _texto_obrigatorio(dados.get("obra_id"), "obra_id")

    session = SessionLocal()
    try:
        obra = session.get(Obra, int(obra_id))
        if obra is None:
            raise ValueError(f"Obra {obra_id} não encontrada.")

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
    url     = _texto_obrigatorio(dados.get("url"), "url")
    obra_id = dados.get("obra_id")
    if not obra_id:
        raise ValueError("O campo 'obra_id' é obrigatório.")
    obra_id = int(obra_id)

    session = SessionLocal()
    try:
        obra = session.get(Obra, obra_id)
        if obra is None:
            raise ValueError(f"Obra {obra_id} não encontrada.")

        pdf = PdfUrl(url=url, obra_id=obra_id)
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        return pdf.to_dict()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
