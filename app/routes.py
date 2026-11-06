"""
Rotas HTML e API HTTP da aplicação InkHub.

Blueprints:
  paginas  -> páginas HTML (/, /login, /logout, /painel)
  api      -> endpoints JSON sob /api/
"""

# Integração de arquivos, respostas HTTP, persistência e autenticação.
import cloudinary.uploader
import flask as fk
from sqlalchemy.exc import IntegrityError

import servico
from werkzeug.security import check_password_hash, generate_password_hash
from database import SessionLocal
from models import Usuario

# ── Blueprints e respostas comuns ──────────────────────────────────────────────

# Agrupa páginas HTML em URLs sem prefixo.
paginas = fk.Blueprint("paginas", __name__)
# Agrupa os endpoints JSON sob o prefixo /api.
api     = fk.Blueprint("api", __name__, url_prefix="/api")


def _erro(mensagem, status=400):
  """Cria uma resposta JSON de erro com o status HTTP informado."""
  return fk.jsonify({"erro": mensagem}), status


def _login_obrigatorio():
  """Retorna redirect se não houver sessão ativa, ou None se ok."""
  if "usuario_id" not in fk.session:
    # Redireciona usuários anônimos para a tela de autenticação.
    return fk.redirect(fk.url_for("paginas.login_get"))
  return None


# ── Páginas públicas e autenticação ───────────────────────────────────────────

@paginas.get("/")
def leitura():
  """Página pública de catálogo / leitura."""
  return fk.render_template("leitura.html")


@paginas.get("/login")
def login_get():
  """Exibe o login, ou envia usuários autenticados ao painel."""
  if "usuario_id" in fk.session:
    return fk.redirect(fk.url_for("paginas.painel"))
  return fk.render_template("login.html", erro=None, email_salvo="")


@paginas.post("/login")
def login_post():
  """Valida credenciais e inicia a sessão do usuário."""
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

  fk.session["usuario_id"]   = usuario["id"]
  fk.session["usuario_nome"] = usuario["nome"]
  return fk.redirect(fk.url_for("paginas.painel"))


@paginas.get("/logout")
def logout():
  """Encerra a sessão atual e retorna ao catálogo."""
  fk.session.clear()
  return fk.redirect(fk.url_for("paginas.leitura"))


# ── Painel protegido ──────────────────────────────────────────────────────────

@paginas.get("/painel")
def painel():
  """Exibe o painel administrativo somente para usuários autenticados."""
  redir = _login_obrigatorio()
  if redir:
    return redir
  return fk.render_template(
    "index.html",
    usuario_nome=fk.session.get("usuario_nome", ""),
  )


# ── API pública de consulta ───────────────────────────────────────────────────

@api.get("/usuarios")
def get_usuarios():
  """Lista os usuários em formato JSON."""
  return fk.jsonify(servico.listar_usuarios())


@api.get("/obras")
def get_obras():
  """Lista as obras disponíveis no catálogo."""
  return fk.jsonify(servico.listar_obras())


@api.get("/capitulos")
def get_capitulos():
  """Lista todos os capítulos cadastrados."""
  return fk.jsonify(servico.listar_capitulos())


@api.get("/pdf_urls")
def get_pdf_urls():
  """Lista os PDFs associados às obras e capítulos."""
  return fk.jsonify(servico.listar_pdf_urls())


# ── Autorização e API de cadastro protegida ───────────────────────────────────

def _api_auth():
  """Retorna resposta 401 se não autenticado, ou None se ok."""
  if "usuario_id" not in fk.session:
    # Mantém o formato de erro consistente para chamadas de API sem login.
    return fk.jsonify({"erro": "Não autenticado."}), 401
  return None


@api.post("/usuarios")
def criar_usuario():
  """Cria usuário via API, exigindo uma sessão autenticada."""
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
  """Cria obra e associa o usuário autenticado como autor."""
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
  """Cria capítulo após validar a propriedade da obra."""
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


# ── API protegida: dados pertencentes ao usuário atual ────────────────────────


@api.get("/minhas_obras")
def get_minhas_obras():
  """Retorna apenas as obras criadas pelo usuário da sessão."""
  negado = _api_auth()
  if negado:
    return negado
  usuario_id = fk.session.get("usuario_id")
  try:
    obras = [o for o in servico.listar_obras() if o.get('autor_id') == usuario_id]
    return fk.jsonify(obras)
  except Exception:
    return fk.jsonify([])


@api.get("/meus_capitulos")
def get_meus_capitulos():
  """Retorna capítulos associados às obras do usuário da sessão."""
  negado = _api_auth()
  if negado:
    return negado
  usuario_id = fk.session.get("usuario_id")
  try:
    minhas = [o['id'] for o in servico.listar_obras() if o.get('autor_id') == usuario_id]
    capitulos = [c for c in servico.listar_capitulos() if c.get('obra_id') in minhas]
    return fk.jsonify(capitulos)
  except Exception:
    return fk.jsonify([])


# ── Registro público a partir da tela de login ────────────────────────────────


@paginas.post("/register")
def register_post():
  """Cadastra uma conta e inicia a sessão após o registro."""
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

  fk.session["usuario_id"] = usuario["id"]
  fk.session["usuario_nome"] = usuario["nome"]
  return fk.redirect(fk.url_for("paginas.painel"))


# ── API protegida para envio e registro de PDF ────────────────────────────────

@api.post("/upload_pdf")
def upload_pdf():
  """Envia PDF ao Cloudinary e registra sua URL vinculada à obra/capítulo."""
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

  # Converte o identificador antes do upload para rejeitar entradas inválidas.
  try:
    obra_id_int = int(obra_id)
  except ValueError:
    return _erro("'obra_id' deve ser um número inteiro.")

  try:
    # Faz upload do fluxo recebido e pede ao Cloudinary uma URL HTTPS pública.
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
    # Persiste a URL retornada e, se presente, associa o PDF a um capítulo.
    dados_pdf = {"url": url_pdf, "obra_id": obra_id_int}
    if capitulo_id:
      dados_pdf["capitulo_id"] = int(capitulo_id)
    registro = servico.cadastrar_pdf_url(dados_pdf)
  except ValueError as e:
    return _erro(str(e))

  return fk.jsonify(registro), 201