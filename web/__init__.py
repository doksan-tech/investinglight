"""Initialize Flask app."""
from flask import Flask

def create_app():
    """application factory"""
    app = Flask(__name__)

    from . import main_views, dash_train
    app.register_blueprint(main_views.bp)
    app.register_blueprint(dash_train.bp)    
    
    return app

# def init_app():
#     """Construct core Flask application."""
#     app = Flask(__name__, instance_relative_config=False)
#     app.config.from_object('config.Config')

#     with app.app_context():
#         # Import parts of our core Flask app
#         from . import routes

#         # Import Dash application
#         from .dash import init_dash
#         app = init_dash(app)
        
#         return app
