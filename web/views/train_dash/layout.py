import pandas as pd
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from web.views.shared_dash import shared_dash_nav
from web.views.getdata import get_data, get_stock_price, get_unique_items

def layout():

    df = get_data('train')
    # output 폴더 내에 아무 파일도 없으면 발생하는 에러 처리
    if df is None:
        train_dash_layout = dbc.Container()
        return train_dash_layout

    unique_df = df.groupby(['stock_code', 'rl_method', 'net', 'lr',
                            'discount_factor', 'start_date', 'end_date',
                            'init_balance']).size().reset_index(name='freq')
    unique_list = []
    for i in unique_df.index:
        unique_list.append(unique_df.iloc[i, :-1].to_list())    # 맨 끝 횟수 제외


    # Create Layout
    train_dash_layout = dbc.Container([
        # dbc.Row(dbc.Col(html.H1('삼성전자 강화학습 결과', 
        #                         className='text-center text-primary mb-2'))),

        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card([
                            dbc.CardBody([
                                html.H5('강화학습 결과', className='card-title mb-3'),
                                dbc.RadioItems(
                                    id="choose_train",
                                    options=[
                                        {'label': [f'{x[0]}, {x[1]}, {x[2]}, {x[5]} ~ {x[6]}', # html.Br(),  TODO: 종목명으로 바꾸기
                                                   f'lr: {x[3]}, df:{x[4]}, 자본금: {x[7]:,}'],
                                         'value': [i for i in x]}
                                        for x in unique_list
                                    ],
                                    value=unique_list[0],
                                ),
                            ]),
                        ], className="mb-2",),
                        dbc.Card(
                            className="mb-2",
                            children=[
                                dbc.CardBody([
                                    # html.H5('삼성전자 주가 차트', className='text-center text-info'),
                                    dcc.Graph(id='candle_chart', figure={}),
                            ]),
                        ]),
                    ], xs=12, sm=12, md=12, lg=5, xl=5,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            className="mb-2",
                            children=[
                                dbc.CardBody([
                                    html.H5('평균 매매 비율', className='text-center text-info'),
                                    dcc.Graph(id='pie_chart', figure={}),
                                    # html.P('에포크를 반복하며 에이전트가 매수, 매도, 관망한 행동을 평균내어 비율화',
                                    #     className='card-text mb-5'),
                            ]),
                        ]),
                        dbc.Card(
                            className="mb-2",
                            children=[
                                dbc.CardBody([
                                    html.H5('누적 학습에 따른 포트폴리오 가치 변화', className='text-center text-info mt-5'),
                                    dcc.Graph(id='pv_chart', figure={}),
                            ]),
                        ]),
                        dbc.Card(
                            className="mb-2",
                            children=[
                                dbc.CardBody([
                                    html.H5('누적 학습에 따른 손실값 변화', className='text-center text-info mt-6'),
                                    dcc.Graph(id='loss_chart', figure={}),
                            ]),
                        ]),

                    ], xs=12, sm=12, md=12, lg=5, xl=5,
                ),
            ], justify="center",
        ),
    ], fluid=True)
    
    return train_dash_layout


layout = html.Div(
    id='train_dash_layout',
    children=[
        shared_dash_nav(),      # 페이지 상단 네이게이션 바
        layout()
    ]
)