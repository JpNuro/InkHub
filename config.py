"""
Configurações da aplicação e integração com o Cloudinary.

As credenciais são lidas do ambiente ou de um arquivo .env local. O exemplo de
upload só é executado quando este arquivo é chamado diretamente como script.
"""

# Bibliotecas e funções usadas para ambiente, carregamento de variáveis e Cloudinary.
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# Carrega variáveis do arquivo .env, se existir, sem substituir as já definidas.
load_dotenv()

# Mantém as credenciais fora do código-fonte, buscando-as nas variáveis de ambiente.
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Caminhos absolutos usados para localizar a pasta de dados da aplicação.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(PROJECT_ROOT, "instance")


class Config:
    """Valores de configuração consumidos pela aplicação Flask."""

    # Chave de sessão e limite máximo de tamanho para uploads.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

    # Disponibiliza as credenciais do Cloudinary na configuração do Flask.
    CLOUDINARY_CLOUD_NAME = CLOUDINARY_CLOUD_NAME
    CLOUDINARY_API_KEY = CLOUDINARY_API_KEY
    CLOUDINARY_API_SECRET = CLOUDINARY_API_SECRET


# Inicializa o cliente Cloudinary para que os módulos da aplicação o reutilizem.
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)


def example_upload():
    """Envia uma imagem de demonstração e imprime URLs com transformações."""
    # Faz upload de um recurso público de demonstração do Cloudinary.
    upload_result = cloudinary.uploader.upload(
        "https://res.cloudinary.com/demo/image/upload/getting-started/shoes.jpg",
        public_id="shoes",
    )
    print(upload_result.get("secure_url"))

    # Gera URLs com formato/qualidade automáticos e com recorte quadrado.
    optimize_url, _ = cloudinary_url("shoes", fetch_format="auto", quality="auto")
    print(optimize_url)

    auto_crop_url, _ = cloudinary_url(
        "shoes", width=500, height=500, crop="auto", gravity="auto"
    )
    print(auto_crop_url)


if __name__ == "__main__":
    # Evita executar o exemplo de upload quando este módulo é apenas importado.
    example_upload()