"""
Rotas da aplicação InkHub.

Blueprints:
  paginas  → páginas HTML  (/, /login, /logout, /painel)
  api      → /api/...  (JSON)
"""

import cloudinary.uploader
import flask as fk
from sqlalchemy.exc import IntegrityError

import servico
from werkzeug.security import check_password_hash, generate_password_hash
from database import SessionLocal
from models import Usuario

# ── Blueprints ────────────────────────────────────────────────────────────────
# Blueprint para páginas HTML
paginas = fk.Blueprint("paginas", __name__)
# Blueprint para API REST
api     = fk.Blueprint("api", __name__, url_prefix="/api")


# Helper para retornar erro JSON
def _erro(mensagem, status=400):
  return fk.jsonify({"erro": mensagem}), status


# Helper para verificar se usuário está logado
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
  # Se já estiver logado, redireciona para o painel
  if "usuario_id" in fk.session:
    return fk.redirect(fk.url_for("paginas.painel"))
  return fk.render_template("login.html", erro=None, email_salvo="")


@paginas.post("/login")
def login_post():
  # Processa o formulário de login
  email = (fk.request.form.get("email") or "").strip()
  senha = (fk.request.form.get("senha") or "").strip()

  usuario = servico.buscar_usuario_por_email(email)

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

  # Cria sessão do usuário
  fk.session["usuario_id"]   = usuario["id"]
  fk.session["usuario_nome"] = usuario["nome"]
  return fk.redirect(fk.url_for("paginas.painel"))


@paginas.get("/logout")
def logout():
  # Limpa a sessão e redireciona para a página inicial
  fk.session.clear()
  return fk.redirect(fk.url_for("paginas.leitura"))


# ── Página protegida ──────────────────────────────────────────────────────────

@paginas.get("/painel")
def painel():
  # Página administrativa protegida (requer login)
  redir = _login_obrigatorio()
  if redir:
    return redir
  return fk.render_template(
    "index.html",
    usuario_nome=fk.session.get("usuario_nome", ""),
  )


# ── API — Leitura (pública) ───────────────────────────────────────────────────
# Endpoints públicos para listar dados

@api.get("/usuarios")
def get_usuarios():
  return fk.jsonify(servico.listar_usuarios())


@api.get("/obras")
def get_obras():
  return fk.jsonify(servico.listar_obras())


@api.get("/capitulos")
def get_capitulos():
  return fk.jsonify(servico.listar_capitulos())


@api.get("/pdf_urls")
def get_pdf_urls():
  return fk.jsonify(servico.listar_pdf_urls())


# ── API — Cadastro (protegido) ────────────────────────────────────────────────
# Endpoints protegidos que requerem autenticação

def _api_auth():
  """Retorna resposta 401 se não autenticado, ou None se ok."""
  if "usuario_id" not in fk.session:
    return fk.jsonify({"erro": "Não autenticado."}), 401
  return None


@api.post("/usuarios")
def criar_usuario():
  # Cria um novo usuário (requer autenticação)
  negado = _api_auth()
  if negado:
    return negado
  dados = fk.request.get_json(silent=True) or {}
  try:
    return fk.jsonify(servico.cadastrar_usuario(dados)), 201
  except ValueError as e:
    return _erro(str(e))
  except IntegrityError:
    return _erro("E-mail já cadastrado.", 409)


@api.post("/obras")
def criar_obra():
  # Cria uma nova obra (requer autenticação)
  negado = _api_auth()
  if negado:
    return negado
  dados = fk.request.get_json(silent=True) or {}
  # garantir que a obra será registrada com o usuário autenticado
  dados["autor_id"] = fk.session.get("usuario_id")
  try:
    return fk.jsonify(servico.cadastrar_obra(dados)), 201
  except ValueError as e:
    return _erro(str(e))


@api.post("/capitulos")
def criar_capitulo():
  # Cria um novo capítulo (requer autenticação)
  negado = _api_auth()
  if negado:
    return negado
  dados = fk.request.get_json(silent=True) or {}
  # passar o id do usuário autenticado para validação de propriedade
  dados["usuario_id"] = fk.session.get("usuario_id")
  try:
    return fk.jsonify(servico.cadastrar_capitulo(dados)), 201
  except ValueError as e:
    return _erro(str(e))


# ── API — Minhas obras / meus capítulos (protegido) ─────────────────────────
# Endpoints para listar dados do usuário autenticado

@api.get("/minhas_obras")
def get_minhas_obras():
  # Lista apenas as obras do usuário autenticado
  negado = _api_auth()
  if negado:
    return negado
  usuario_id = fk.session.get("usuario_id")
  try:
    # filtra obras por autor_id
    obras = [o for o in servico.listar_obras() if o.get('autor') and (o.get('autor_id') == usuario_id or o.get('autor') == fk.session.get('usuario_nome'))]
    return fk.jsonify(obras)
  except Exception:
    return fk.jsonify([])


@api.get("/meus_capitulos")
def get_meus_capitulos():
  # Lista apenas os capítulos das obras do usuário autenticado
  negado = _api_auth()
  if negado:
    return negado
  usuario_id = fk.session.get("usuario_id")
  try:
    minhas = []
    for o in servico.listar_obras():
      if o.get('autor_id') == usuario_id or o.get('autor') == fk.session.get('usuario_nome'):
        minhas.append(o['id'])
    capitulos = [c for c in servico.listar_capitulos() if c.get('obra_id') in minhas]
    return fk.jsonify(capitulos)
  except Exception:
    return fk.jsonify([])


# ── Registro público na tela de login ─────────────────────────────────────────

@paginas.post("/register")
def register_post():
  # Processa o formulário de cadastro público na tela de login
  if "usuario_id" in fk.session:
    return fk.redirect(fk.url_for("paginas.painel"))
  nome = (fk.request.form.get("nome") or "").strip()
  email = (fk.request.form.get("email") or "").strip()
  senha = (fk.request.form.get("senha") or "").strip()
  try:
    usuario = servico.cadastrar_usuario({"nome": nome, "email": email, "senha": senha})
  except IntegrityError:
    return fk.render_template("login.html", erro="E-mail já cadastrado.", email_salvo=email), 409
  except ValueError as e:
    return fk.render_template("login.html", erro=str(e), email_salvo=email), 400

  # Cria sessão do novo usuário
  fk.session["usuario_id"] = usuario["id"]
  fk.session["usuario_nome"] = usuario["nome"]
  return fk.redirect(fk.url_for("paginas.painel"))


# ── API — Upload de PDF (protegido) ──────────────────────────────────────────

@api.post("/upload_pdf")
def upload_pdf():
  # Faz upload de PDF para o Cloudinary e salva a URL no banco
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
    # Upload para o Cloudinary
    resultado = cloudinary.uploader.upload(
      arquivo.stream,
      resource_type="image",
      folder="inkhub/pdfs",
      use_filename=True,
      unique_filename=True,
      overwrite=False,
    )
    url_pdf = resultado["secure_url"]
  except Exception as e:
    return _erro(f"Falha no upload para o Cloudinary: {e}", 502)

  try:
    # Salva a URL do PDF no banco de dados
    dados_pdf = {"url": url_pdf, "obra_id": obra_id_int}
    if capitulo_id:
      dados_pdf["capitulo_id"] = int(capitulo_id)
    registro = servico.cadastrar_pdf_url(dados_pdf)
  except ValueError as e:
    return _erro(str(e))

  return fk.jsonify(registro), 201