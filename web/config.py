"""Flask config."""
import os
from dotenv import load_dotenv  # pip install python-dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_BASE_DIR = os.path.join(BASE_DIR, os.path.pardir)

load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    """Flask configuration variables."""

    # General Config
    APP_NAME = os.environ.get("APP_NAME")
    DEBUG = os.environ.get("FLASK_DEBUG")
    
    # Static Assets
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
