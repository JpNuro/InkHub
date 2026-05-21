"""
Rotas da aplicação InkHub.

Blueprints:
  paginas  → páginas HTML  (/, /login, /logout, /painel)
  api      → /api/...  (JSON)
"""

import cloudinary.uploader
import flask as fk
from sqlalchemy.exc import IntegrityError

import servicos
from werkzeug.security import check_password_hash, generate_password_hash
from database import SessionLocal
from models import Usuario

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

    if usuario is None:
        return fk.render_template(
            "login.html",
            erro="E-mail ou senha incorretos.",
            email_salvo=email,
        ), 401

    stored = usuario.get("senha") or ""
    ok = False
    # detectar formatos de hash comuns e usar check_password_hash; caso contrário, comparar texto plano
    if stored.startswith("pbkdf2:") or stored.startswith("scrypt:") or stored.startswith("argon2:"):
        ok = check_password_hash(stored, senha)
    else:
        ok = (stored == senha)
        # se a senha no banco era texto plano e confere, migrar para hash
        if ok:
            session = SessionLocal()
            try:
                u = session.get(Usuario, usuario["id"])
                if u is not None:
                    u.senha = generate_password_hash(senha)
                    session.add(u)
                    session.commit()
            finally:
                session.close()

    if not ok:
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
    # garantir que a obra será registrada com o usuário autenticado
    dados["autor_id"] = fk.session.get("usuario_id")
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
    # passar o id do usuário autenticado para validação de propriedade
    dados["usuario_id"] = fk.session.get("usuario_id")
    try:
        return fk.jsonify(servicos.cadastrar_capitulo(dados)), 201
    except ValueError as e:
        return _erro(str(e))


# ── API — Minhas obras / meus capítulos (protegido) ─────────────────────────


@api.get("/minhas_obras")
def get_minhas_obras():
    negado = _api_auth()
    if negado:
        return negado
    usuario_id = fk.session.get("usuario_id")
    try:
        # filtra obras por autor_id
        session = servicos.SessionLocal if hasattr(servicos, 'SessionLocal') else None
        obras = [o for o in servicos.listar_obras() if o.get('autor') and (o.get('autor_id') == usuario_id or o.get('autor') == fk.session.get('usuario_nome'))]
        return fk.jsonify(obras)
    except Exception:
        return fk.jsonify([])


@api.get("/meus_capitulos")
def get_meus_capitulos():
    negado = _api_auth()
    if negado:
        return negado
    usuario_id = fk.session.get("usuario_id")
    try:
        minhas = []
        for o in servicos.listar_obras():
            if o.get('autor_id') == usuario_id or o.get('autor') == fk.session.get('usuario_nome'):
                minhas.append(o['id'])
        capitulos = [c for c in servicos.listar_capitulos() if c.get('obra_id') in minhas]
        return fk.jsonify(capitulos)
    except Exception:
        return fk.jsonify([])


# ── Registro público na tela de login


@paginas.post("/register")
def register_post():
    if "usuario_id" in fk.session:
        return fk.redirect(fk.url_for("paginas.painel"))
    nome = (fk.request.form.get("nome") or "").strip()
    email = (fk.request.form.get("email") or "").strip()
    senha = (fk.request.form.get("senha") or "").strip()
    try:
        usuario = servicos.cadastrar_usuario({"nome": nome, "email": email, "senha": senha})
    except IntegrityError:
        return fk.render_template("login.html", erro="E-mail já cadastrado.", email_salvo=email), 409
    except ValueError as e:
        return fk.render_template("login.html", erro=str(e), email_salvo=email), 400

    fk.session["usuario_id"] = usuario["id"]
    fk.session["usuario_nome"] = usuario["nome"]
    return fk.redirect(fk.url_for("paginas.painel"))


# ── API — Upload de PDF (protegido) ──────────────────────────────────────────

@api.post("/upload_pdf")
def upload_pdf():
    negado = _api_auth()
    if negado:
        return negado

    arquivo = fk.request.files.get("arquivo")
    obra_id = fk.request.form.get("obra_id")
    capitulo_id = fk.request.form.get("capitulo_id")

    if not arquivo or arquivo.filename == "":
        return _erro("Nenhum arquivo enviado.")
    if not arquivo.filename.lower().endswith(".pdf"):
        return _erro("Apenas arquivos PDF são aceitos.")
    if not obra_id:
        return _erro("O campo 'obra_id' é obrigatório.")

    try:
        obra_id_int = int(obra_id)
    except ValueError:
        return _erro("'obra_id' deve ser um número inteiro.")

    try:
        resultado = cloudinary.uploader.upload(
            arquivo.stream,
            resource_type="raw",
            folder="inkhub/pdfs",
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )
        url_pdf = resultado["secure_url"]
    except Exception as e:
        return _erro(f"Falha no upload para o Cloudinary: {e}", 502)

    try:
        dados_pdf = {"url": url_pdf, "obra_id": obra_id_int}
        if capitulo_id:
            dados_pdf["capitulo_id"] = int(capitulo_id)
        registro = servicos.cadastrar_pdf_url(dados_pdf)
    except ValueError as e:
        return _erro(str(e))

    return fk.jsonify(registro), 201