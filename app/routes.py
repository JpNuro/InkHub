import flask as fk
from sqlalchemy.exc import IntegrityError

from servicos import (
    cadastrar_usuario,
    cadastrar_obra,
    cadastrar_capitulo,
    listar_usuarios,
    listar_obras,
    listar_capitulos,
)

bp = fk.Blueprint("api", __name__, url_prefix="/api")


def _erro(mensagem, status=400):
    return fk.jsonify({"erro": mensagem}), status


@bp.get("/usuarios")
def usuarios():
    return fk.jsonify(listar_usuarios())


@bp.post("/usuarios")
def criar_usuario():
    dados = fk.request.get_json(silent=True) or {}
    try:
        return fk.jsonify(cadastrar_usuario(dados)), 201
    except ValueError as exc:
        return _erro(str(exc))
    except IntegrityError:
        return _erro("Já existe um usuário com este e-mail.", 409)


@bp.get("/obras")
def obras():
    return fk.jsonify(listar_obras())


@bp.post("/obras")
def criar_obra():
    dados = fk.request.get_json(silent=True) or {}
    try:
        return fk.jsonify(cadastrar_obra(dados)), 201
    except ValueError as exc:
        return _erro(str(exc))
    except IntegrityError:
        return _erro("Erro de integridade ao salvar a obra.", 409)


@bp.get("/capitulos")
def capitulos():
    return fk.jsonify(listar_capitulos())


@bp.post("/capitulos")
def criar_capitulo():
    dados = fk.request.get_json(silent=True) or {}
    try:
        return fk.jsonify(cadastrar_capitulo(dados)), 201
    except ValueError as exc:
        return _erro(str(exc))
    except IntegrityError:
        return _erro("Erro de integridade ao salvar o capítulo.", 409)


paginas = fk.Blueprint("paginas", __name__)


@paginas.get("/")
def home():
    return fk.render_template("index.html")
