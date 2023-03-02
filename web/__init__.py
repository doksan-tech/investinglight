"""Initialize Flask app."""
from flask import Flask
# import config

def create_app(dash_debug, dash_auto_reload):
    """application factory"""
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_object('config.Config')
    
    from web.views import main_views, train_dash, test_dash
    app.register_blueprint(main_views.bp)
    app = train_dash.init_dash(app)
    app = test_dash.init_dash(app)
    
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
