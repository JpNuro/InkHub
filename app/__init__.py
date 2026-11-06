"""
Fábrica da aplicação Flask e configuração das extensões/rotas.
"""

# Integração externa usada para armazenar os PDFs enviados pelo painel.
import cloudinary

# Aplicação WSGI que serve templates, arquivos estáticos e endpoints.
from flask import Flask

# Configurações e credenciais carregadas do ambiente.
from config import (
    Config,
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)
# Engine e metadados do SQLAlchemy usados para preparar as tabelas.
from database import Base, engine


def create_app():
    """Monta e retorna uma instância configurada do aplicativo Flask."""
    # Cria tabelas que ainda não existem (não apaga dados)
    Base.metadata.create_all(bind=engine)

    # Define as pastas usadas pelo Flask para templates e arquivos estáticos.
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    # Define o limite de requisições para suportar uploads de PDF.
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB por upload

    # Configura Cloudinary
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )

    # Importa no momento da inicialização para evitar ciclo de importação.
    from app.routes import api, paginas
    # Registra separadamente as páginas HTML e os endpoints JSON.
    app.register_blueprint(api)
    app.register_blueprint(paginas)

    return app