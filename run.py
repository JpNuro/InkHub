"""
Ponto de entrada da aplicação InkHub.

Este arquivo cria a aplicação Flask e inicia o servidor de desenvolvimento.
"""

from app import create_app

# Cria a instância da aplicação Flask
app = create_app()

# ── Inicialização do Servidor ───────────────────────────────────────────────────
if __name__ == "__main__":
    # Inicia o servidor de desenvolvimento em modo debug
    # debug=True: recarrega automaticamente quando há alterações nos arquivos
    # host='0.0.0.0': permite acesso externo (não apenas localhost)
    # port=5000: porta onde o servidor vai rodar
    app.run(debug=True, host='0.0.0.0', port=5000)
