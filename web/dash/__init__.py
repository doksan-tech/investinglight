"""Instantiate a Dash app."""
from dash import Dash, html, dcc, dash_table


def init_dash(server):
    """Create a Plotly Dash dashboard."""
    dash_app = Dash(
        server=server,
        routes_pathname_prefix="/learnchart/",
        # external_stylesheets=[
        #     "/static/dist/css/styles.css",
        #     "https://fonts.googleapis.com/css?family=Lato",
        # ],
    )
    
    # Load DataFrame
    
    # Create Layout
    dash_app.layout = html.Div(
        html.H1('Hello Dash')
    )
    
    
    
    return dash_app.server