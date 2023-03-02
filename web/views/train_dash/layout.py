from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from web.views.shared_dash import shared_dash_nav

def layout():
    pass
    
    
layout = html.Div(
    id='train_dash_layout',
    children=[shared_dash_nav(),
              layout()]
)