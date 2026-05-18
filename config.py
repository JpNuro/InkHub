import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")

# import os

# BASE_DIR     = os.path.abspath(os.path.dirname(__file__))
# INSTANCE_DIR = os.path.join(BASE_DIR, "instance")


# class Config:
#     SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me")


# # ── Cloudinary ──────────────────────────────────────────────────────────────
# # Crie conta gratuita em https://cloudinary.com e copie as credenciais do
# # painel "Dashboard" → "Product Environment Credentials"
# CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "SEU_CLOUD_NAME")
# CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "SUA_API_KEY")
# CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "SEU_API_SECRET")