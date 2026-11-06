# Importa a fábrica que configura rotas, extensões e banco de dados.
from app import create_app

# Cria a aplicação Flask usada pelo servidor de desenvolvimento.
app = create_app()

if __name__ == "__main__":
    # Permite executar o projeto diretamente com `python run.py`.
    app.run(debug=True, host='0.0.0.0', port=5000)
