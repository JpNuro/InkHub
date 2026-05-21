
"""Cloudinary configuration.

Reads credentials from environment variables (optionally from a .env file).
This file no longer performs uploads on import; run as a script for the example usage.
"""

import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# Load .env if present
load_dotenv()

# Read credentials from environment, falling back to the previous defaults
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(PROJECT_ROOT, "instance")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    CLOUDINARY_CLOUD_NAME = CLOUDINARY_CLOUD_NAME
    CLOUDINARY_API_KEY = CLOUDINARY_API_KEY
    CLOUDINARY_API_SECRET = CLOUDINARY_API_SECRET

# Configuration
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)


def example_upload():
    """Example: upload and show transformed URLs when run as a script."""
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