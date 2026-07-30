"""
Configurações da aplicação InkHub.

Inclui:
- Configuração do Cloudinary para upload de PDFs
- Configuração do Flask (chave secreta, limite de upload)
- Caminhos do projeto
"""

import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# Carrega variáveis de ambiente do arquivo .env se existir
load_dotenv()

# ── Credenciais do Cloudinary ───────────────────────────────────────────────────
# Lê as credenciais do Cloudinary das variáveis de ambiente
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# ── Caminhos do Projeto ───────────────────────────────────────────────────────────
# Diretório raiz do projeto
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
# Diretório instance para arquivos de dados
INSTANCE_DIR = os.path.join(PROJECT_ROOT, "instance")

# ── Classe de Configuração do Flask ───────────────────────────────────────────────
class Config:
    """Configurações da aplicação Flask."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")  # Chave secreta para sessões
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # Limite de upload: 50 MB
    CLOUDINARY_CLOUD_NAME = CLOUDINARY_CLOUD_NAME
    CLOUDINARY_API_KEY = CLOUDINARY_API_KEY
    CLOUDINARY_API_SECRET = CLOUDINARY_API_SECRET

# ── Configuração do Cloudinary ───────────────────────────────────────────────────
# Configura o SDK do Cloudinary com as credenciais
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)


# ── Função de Exemplo ───────────────────────────────────────────────────────────
def example_upload():
    """Exemplo: upload e transformação de imagens quando executado como script."""
    upload_result = cloudinary.uploader.upload(
        "https://res.cloudinary.com/demo/image/upload/getting-started/shoes.jpg",
        public_id="shoes",
    )
    print(upload_result.get("secure_url"))

    optimize_url, _ = cloudinary_url("shoes", fetch_format="auto", quality="auto")
    print(optimize_url)

    auto_crop_url, _ = cloudinary_url(
        "shoes", width=500, height=500, crop="auto", gravity="auto"
    )
    print(auto_crop_url)


if __name__ == "__main__":
    example_upload()