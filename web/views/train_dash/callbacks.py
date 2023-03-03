import pandas as pd
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from web.views.getdata import get_data, get_stock_price, get_unique_items


def register_callbacks(dash_app):
    pass
    # log_df = get_data('train')
    # stock_code_list = get_unique_items(log_df, 'stockcode')
    # rl_list = get_unique_items(log_df, 'rl_method')
    # net_list = get_unique_items(log_df, 'net')
    
    # @dash_app.callback(
    #     Output(component_id='pie_chart', component_property='figure'),
    #     [Input(component_id='choose_rl_method', component_property='value'),
    #      Input(component_id='choose_net', component_property='value')]
    # )
    # def update_pie(rl_method, net):
    #     df_trading = log_df.loc[:, ['num_buy', 'num_sell', 'num_hold']]
    #     df_trading = df_trading.astype('int')
    #     labels = ['매수', '매도', '관망']
    #     values = [df_trading['num_buy'].mean(), df_trading['num_sell'].mean(), df_trading['num_hold'].mean()]
    #     pie_chart = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent', hole=.3)])
    #     pie_chart.update_layout(
    #         showlegend=False,
    #         annotations=[dict(text='매매', x=0.5, y=0.5, font_size=15, showarrow=False)],
    #         font={'size':13},
    #         height=300,
    #         margin_autoexpand=False,
    #         margin=dict(t=20, b=20, l=10, r=10)
    #     )
    
    #     return pie_chart



# def register_callbacks(dash_app):
#     @dash_app.callback(
#         Output('indicator-graphic', 'figure'),
#         [Input('xaxis-column', 'value'),
#          Input('yaxis-column', 'value'),
#          Input('xaxis-type', 'value'),
#          Input('yaxis-type', 'value'),
#          Input('year--slider', 'value')])
#     def update_graph(xaxis_column_name, yaxis_column_name,
#                      xaxis_type, yaxis_type,
#                      year_value):
#         df = Data.get_raw()
#         dff = df[df['Year'] == year_value]

#         fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
#                          y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
#                          hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

#         fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

#         fig.update_xaxes(title=xaxis_column_name,
#                          type='linear' if xaxis_type == 'Linear' else 'log')

#         fig.update_yaxes(title=yaxis_column_name,
#                          type='linear' if yaxis_type == 'Linear' else 'log')

#         return fig