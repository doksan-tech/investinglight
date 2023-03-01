"""Instantiate a Dash app."""
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
        routes_pathname_prefix="/learnchart/",
        # external_stylesheets=[
        #     "/static/dist/css/styles.css",
        #     "https://fonts.googleapis.com/css?family=Lato",
        # ],
    )
    
    # Load DataFrame
    stock_df, log_df, params, learner, result = getdata('epoch.log')

    # Candle chart
    # stock_df = stock_df.reset_index(drop=True)
    stock_df['date'] = stock_df['date'].apply(lambda x: str(x))
    candle_chart = go.Figure(
        data=[go.Candlestick(
            x=[f'[{i[:4]}/{i[4:6]}/{i[6:8]}]' for i in stock_df['date']],
            open=stock_df['open'], high=stock_df['high'], low=stock_df['low'], close=stock_df['close'],
            text=[f'거래량: {i:,}' for i in stock_df['volume']],
            increasing_line_color= 'red', decreasing_line_color= 'blue')]
    )
    candle_chart.update_layout(
        xaxis_rangeslider_visible=False,
        margin=dict(t=20, b=20, l=10, r=10),
        font={'size':10},
    )
    
    # pie chart
    df_trading = log_df.loc[:, ['num_buy', 'num_sell', 'num_hold']]
    df_trading = df_trading.astype('int')
    labels = ['매수', '매도', '관망']
    values = [df_trading['num_buy'].mean(), df_trading['num_sell'].mean(), df_trading['num_hold'].mean()]
    pie_chart = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent', hole=.3)])
    pie_chart.update_layout(
        showlegend=False,
        annotations=[dict(text='매매', x=0.5, y=0.5, font_size=15, showarrow=False)],
        font={'size':13},
        height=300,
        margin_autoexpand=False,
        margin=dict(t=20, b=20, l=10, r=10)
    )
    
    # PV chart
    df_pv = log_df.loc[:, ['epochs', 'pv', 'loss']]
    df_pv = df_pv.astype('float')
    pv_chart = px.line(df_pv, x='epochs', y='pv')
    pv_chart.add_hline(y=int(params['balance']), line_width=1, line_color="red")
    pv_chart.update_layout(
        font={'size':10},
        margin=dict(t=20, b=20, l=10, r=10),
        height=400,
        paper_bgcolor="#fff", plot_bgcolor="#fff"
    )
    pv_chart.update_xaxes(showline=True, linewidth=2, linecolor='Lightgray', mirror=True)
    pv_chart.update_yaxes(range=[int(params['balance'])*0.5, int(params['balance'])*2], 
                        dtick=10_000_000, ticklabelstep=2,
                        gridcolor='Lightgray')

    # loss chart
    loss_chart = px.line(df_pv, x='epochs', y='loss')
    loss_chart.update_layout(
        font={'size':10},
        margin=dict(t=20, b=20, l=10, r=10),
        height=400,
        paper_bgcolor="#fff", plot_bgcolor="#fff")
    loss_chart.update_xaxes(showline=True, linewidth=2, linecolor='Lightgray', mirror=True)
    loss_chart.update_yaxes(range=[0.5, 0.8], gridcolor='Lightgray')
    
    # Create Layout
    dash_app.layout = dbc.Container([
        dbc.Row(dbc.Col(html.H1('삼성전자 강화학습 결과', 
                                className='text-center text-primary mb-2'))),
        
        dbc.Row(dbc.Col(html.Div(
            f"{params['stock_code']} #학습기간: {params['start_date']} ~ {params['end_date']} #강화학습: {params['rl_method']} #신경망: {params['net']} #learning rate: {params['lr']} #discount factor: {params['discount_factor']}",
            className='mb-4'), width={'size':12, 'offset':1})),
        
        dbc.Row([
            dbc.Col([
                html.H3('삼성전자 주가 차트', className='text-center text-danger mb-5'),
                dcc.Graph(figure=candle_chart),
            ], xs=12, sm=12, md=12, lg=8, xl=8 ),  # 작은 화면에서는 12칸 모두 사용하고, 큰 화면에서는 8칸 사용
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3('평균 매매 비율', className='text-center text-danger'),
                        dcc.Graph(figure=pie_chart),
                        html.P('에포크를 반복하며 에이전트가 매수, 매도, 관망한 행동을 평균내어 비율화', 
                               className='card-text mb-5'),
                    ]),
                ]),
            ], xs=12, sm=12, md=12, lg=4, xl=4 ),
        ], justify="around", align="start"),
        
        dbc.Row([
            dbc.Col([
                html.H3('누적 학습에 따른 포트폴리오 가치 변화', className='text-center text-danger mt-5'),
                dcc.Graph(figure=pv_chart),
            ], xs=12, sm=12, md=12, lg=6, xl=6),
            dbc.Col([
                html.H3('누적 학습에 따른 손실값 변화', className='text-center text-danger mt-5'),
                dcc.Graph(figure=loss_chart),
            ], xs=12, sm=12, md=12, lg=6, xl=6),
        ], justify="around", align="loss_chart"),
    ], fluid=True)
    
    return dash_app.server
