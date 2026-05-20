"""
Factory da aplicação Flask.
"""

import cloudinary

from flask import Flask

from config import (
    Config,
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)
from database import Base, engine


def create_app():
    # Cria tabelas que ainda não existem (não apaga dados)
    Base.metadata.create_all(bind=engine)

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB por upload

    # Configura Cloudinary
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )

    # Blueprints
    from app.routes import api, paginas
    app.register_blueprint(api)
    app.register_blueprint(paginas)

    return app