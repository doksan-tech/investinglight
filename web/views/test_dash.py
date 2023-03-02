import os
import pandas as pd
from dash import Dash, html, dcc            # 2.8.1
import plotly.express as px                 # 5.13.0
import plotly.graph_objects as go
import dash_bootstrap_components as dbc     # 1.3.1

from .getdata import getdata

def init_dash(server):
    """Create a Plotly Dash dashboard."""
    dash_app = Dash(
        external_stylesheets=[dbc.themes.BOOTSTRAP], 
        meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}], 
        server=server,
        routes_pathname_prefix="/test/",
        # external_stylesheets=[
        #     "/static/dist/css/styles.css",
        #     "https://fonts.googleapis.com/css?family=Lato",
        # ],
    )
    
    dash_app.layout = html.Div(
        children=[html.H1(children="TEST Dash")], className="container-fluid"
    )
    
    return dash_app.server

if __name__ == "__main__":
    app = Dash(__name__)
    app.run_server(debug=True)