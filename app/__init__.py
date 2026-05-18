from flask import Flask
from .routes import paginas, api


def create_app():
    app = Flask(__name__)
    # app.secret_key = 'sua-chave-secreta-aqui'  # Configurado via Config
    
    app.register_blueprint(paginas)
    app.register_blueprint(api)
    
    return app
