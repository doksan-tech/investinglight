# import dash_html_components as html, dcc
# import dash_bootstrap_components as dbc


# def shared_dash_nav() -> html.Div:
#     link_style = {'marginLeft': '10px'}
#     links = html.Div
#     (
#         id='shared-dash-nav',
#         # style={'display': 'flex', 'flexWrap': 'wrap', 'marginTop': '15px', 'marginBottom': '15px', 'backgroundColor': 'lightBlue'},
#         html.Div
#         (
#             class_name="navbar navbar-expand-lg navbar-light bg-light border-bottom",
                 
#         )
#     )
#     return links

from dash import html

def shared_dash_nav() -> html.Div:
    link_style = {'marginLeft': '10px'}
    links = html.Div(
        id='shared-navigation-links',
        # style={'display': 'flex', 'flexWrap': 'wrap', 'marginTop': '15px', 'marginBottom': '15px', 'backgroundColor': 'lightBlue'},
        className="navbar navbar-expand-lg navbar-light bg-light border-bottom",
        children=[
            html.Div(
                className="container-fluid",
                children=[
                    html.A(
                        href='/',
                        children='투자 신호등',
                        className="navbar-brand"
                    ),
                    html.Div(
                        className="navbar-nav me-auto mb-2 mb-lg-0 nav-item",
                        children=[
                            html.A(
                                href='/register',
                                children='에이전트 훈련',
                                className="nav-link"
                            ),
                            html.A(
                                href='/train',
                                children='에이전트 훈련 결과',
                                className="nav-link"
                            ),
                            html.A(
                                href='/test',
                                children='에이전트 테스트 결과',
                                className="nav-link"
                            ),
                        ]
                    )
                ]
            )
        ]
    )
    return links