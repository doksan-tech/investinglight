"""Flask config."""
from os import environ, path
from dotenv import load_dotenv  # pip install python-dotenv

BASE_DIR = path.abspath(path.dirname(__file__))
load_dotenv(path.join(BASE_DIR, ".env"))

class Config:
    """Flask configuration variables."""

    # General Config
    FLASK_APP = "wsgi.py"
    FLASK_ENV = environ.get("FLASK_DEBUG")
    
    # Static Assets
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    COMPRESSOR_DEBUG = environ.get("COMPRESSOR_DEBUG")