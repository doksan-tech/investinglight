# keep this file and other files used by the create_app function free of inner-project import statements to help
# prevent circular imports.  Setting up cache in a separate cache.py file similar to this config.py file is very helpful.
import os
from dotenv import load_dotenv  # pip install python-dotenv

# BASE_DIR = os.path.abspath(os.path.join(__file__, os.path.pardir))  # project home
BASE_DIR = os.path.abspath(os.path.join(__file__))  # project home
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Config:
    # user configurations
    flask_debug = True
    dash_debug = False
    dash_auto_reload = False

    # flask configurations
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Static Assets
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"

