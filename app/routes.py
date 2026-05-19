"""
Rotas da aplicação InkHub.

Blueprints:
  paginas  → páginas HTML  (/, /login, /logout, /painel)
  api      → /api/...  (JSON)
"""

#import cloudinary.uploader
import flask as fk
from sqlalchemy.exc import IntegrityError

import servicos

# ── Blueprints ────────────────────────────────────────────────────────────────

paginas = fk.Blueprint("paginas", __name__)
api     = fk.Blueprint("api", __name__, url_prefix="/api")


def _erro(mensagem, status=400):
    return fk.jsonify({"erro": mensagem}), status


def _login_obrigatorio():
    """Retorna redirect se não houver sessão ativa, ou None se ok."""
    if "usuario_id" not in fk.session:
        return fk.redirect(fk.url_for("paginas.login_get"))
    return None


# ── Páginas públicas ──────────────────────────────────────────────────────────

@paginas.get("/")
def leitura():
    """Página pública de catálogo / leitura."""
    return fk.render_template("leitura.html")


@paginas.get("/login")
def login_get():
    if "usuario_id" in fk.session:
        return fk.redirect(fk.url_for("paginas.painel"))
    return fk.render_template("login.html", erro=None, email_salvo="")


@paginas.post("/login")
def login_post():
    email = (fk.request.form.get("email") or "").strip()
    senha = (fk.request.form.get("senha") or "").strip()

    usuario = servicos.buscar_usuario_por_email(email)

    if usuario is None or usuario.get("senha") != senha:
        return fk.render_template(
            "login.html",
            erro="E-mail ou senha incorretos.",
            email_salvo=email,
        ), 401

    fk.session["usuario_id"]   = usuario["id"]
    fk.session["usuario_nome"] = usuario["nome"]
    return fk.redirect(fk.url_for("paginas.painel"))


@paginas.get("/logout")
def logout():
    fk.session.clear()
    return fk.redirect(fk.url_for("paginas.leitura"))


# ── Página protegida ──────────────────────────────────────────────────────────

@paginas.get("/painel")
def painel():
    redir = _login_obrigatorio()
    if redir:
        return redir
    return fk.render_template(
        "index.html",
        usuario_nome=fk.session.get("usuario_nome", ""),
    )


# ── API — Leitura (pública) ───────────────────────────────────────────────────

@api.get("/usuarios")
def get_usuarios():
    return fk.jsonify(servicos.listar_usuarios())


@api.get("/obras")
def get_obras():
    return fk.jsonify(servicos.listar_obras())


@api.get("/capitulos")
def get_capitulos():
    return fk.jsonify(servicos.listar_capitulos())


@api.get("/pdf_urls")
def get_pdf_urls():
    return fk.jsonify(servicos.listar_pdf_urls())


# ── API — Cadastro (protegido) ────────────────────────────────────────────────

def _api_auth():
    """Retorna resposta 401 se não autenticado, ou None se ok."""
    if "usuario_id" not in fk.session:
        return fk.jsonify({"erro": "Não autenticado."}), 401
    return None


@api.post("/usuarios")
def criar_usuario():
    negado = _api_auth()
    if negado:
        return negado
    dados = fk.request.get_json(silent=True) or {}
    try:
        return fk.jsonify(servicos.cadastrar_usuario(dados)), 201
    except ValueError as e:
        return _erro(str(e))
    except IntegrityError:
        return _erro("E-mail já cadastrado.", 409)


@api.post("/obras")
def criar_obra():
    negado = _api_auth()
    if negado:
        return negado
    dados = fk.request.get_json(silent=True) or {}
    try:
        return fk.jsonify(servicos.cadastrar_obra(dados)), 201
    except ValueError as e:
        return _erro(str(e))


@api.post("/capitulos")
def criar_capitulo():
    negado = _api_auth()
    if negado:
        return negado
    dados = fk.request.get_json(silent=True) or {}
    try:
        return fk.jsonify(servicos.cadastrar_capitulo(dados)), 201
    except ValueError as e:
        return _erro(str(e))


# ── API — Upload de PDF (protegido) ──────────────────────────────────────────

# @api.post("/upload_pdf")
# def upload_pdf():
#     negado = _api_auth()
#     if negado:
#         return negado

#     arquivo = fk.request.files.get("arquivo")
#     obra_id = fk.request.form.get("obra_id")

#     if not arquivo or arquivo.filename == "":
#         return _erro("Nenhum arquivo enviado.")
#     if not arquivo.filename.lower().endswith(".pdf"):
#         return _erro("Apenas arquivos PDF são aceitos.")
#     if not obra_id:
#         return _erro("O campo 'obra_id' é obrigatório.")

#     try:
#         obra_id_int = int(obra_id)
#     except ValueError:
#         return _erro("'obra_id' deve ser um número inteiro.")

#     try:
#         resultado = cloudinary.uploader.upload(
#             arquivo.stream,
#             resource_type="raw",
#             folder="inkhub/pdfs",
#             use_filename=True,
#             unique_filename=True,
#             overwrite=False,
#         )
#         url_pdf = resultado["secure_url"]
#     except Exception as e:
#         return _erro(f"Falha no upload para o Cloudinary: {e}", 502)

#     try:
#         registro = servicos.cadastrar_pdf_url({"url": url_pdf, "obra_id": obra_id_int})
#     except ValueError as e:
#         return _erro(str(e))

#     return fk.jsonify(registro), 201
