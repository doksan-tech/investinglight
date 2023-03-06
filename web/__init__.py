"""Initialize Flask app."""
import os
from flask import Flask
from flask.helpers import get_root_path
from dash import Dash
import dash_bootstrap_components as dbc

def create_app(dash_debug, dash_auto_reload):
    """application factory"""
    server = Flask(__name__, instance_relative_config=True)
    server.config.from_object('config.Config')
    
    # register all dash apps and blueprint -------------------
    from web.views import main_views, train_dash, test_dash
    # register blueprint
    server.register_blueprint(main_views.bp)
    
    # register train_dash
    from .views.train_dash.layout import layout as train_dash_layout
    from .views.train_dash.callbacks import register_callbacks as train_dash_callbacks
    register_dash_app(
        flask_server=server,
        title='Train Result',
        base_pathname='train',
        layout=train_dash_layout,
        register_callbacks_funcs=[train_dash_callbacks],
        dash_debug=dash_debug,
        dash_auto_reload=dash_auto_reload
    )
    
    # register test_dash
    # server = test_dash.init_dash(server)
    from .views.test_dash.layout import layout as test_dash_layout
    from .views.test_dash.callbacks import register_callbacks as test_dash_callbacks
    register_dash_app(
        flask_server=server,
        title='Test Result',
        base_pathname='test',
        layout=test_dash_layout,
        register_callbacks_funcs=[test_dash_callbacks],
        dash_debug=dash_debug,
        dash_auto_reload=dash_auto_reload
    )
    
    # if running on gunicorn with multiple workers this message should print once for each worker if preload_app is set to False
    print(f'Flask With Dash Apps Built Successfully with PID {str(os.getpid())}.')
    
    return server


def register_dash_app(flask_server, title, base_pathname, 
                      layout, register_callbacks_funcs, 
                      dash_debug, dash_auto_reload):
    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", 
                     "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    my_dash_app = Dash(
        __name__,
        server=flask_server,
        url_base_pathname=f'/{base_pathname}/',
        assets_folder=get_root_path(__name__) + '/static/',
        meta_tags=[meta_viewport],
        external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP],
        # external_scripts=[]
    )

    with flask_server.app_context():
        my_dash_app.title = title
        my_dash_app.layout = layout
        my_dash_app.css.config.serve_locally = True
        my_dash_app.enable_dev_tools(debug=dash_debug, dev_tools_hot_reload=dash_auto_reload)
        for call_back_func in register_callbacks_funcs:
            call_back_func(my_dash_app)
