import pandas as pd
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from web.views.shared_dash import shared_dash_nav
from web.views.getdata import get_data, get_stock_price, get_unique_items

def layout():
    
    log_df = get_data('train')
    stock_code_list = get_unique_items(log_df, 'stockcode')  # TODO: 여러 종목일 경우 각각의 데이터를 어떻게 처리??
    rl_list = get_unique_items(log_df, 'rl_method')
    net_list = get_unique_items(log_df, 'net')
    
    stock_df = get_stock_price(stock_code_list[0], 20210101, 20210930)  # TODO: 매개변수 수정
    stock_names = pd.unique(stock_df['stockname'])

    # candle chart
    stock_df['date'] = stock_df['date'].apply(lambda x: str(x))
    candle_chart = go.Figure(
        data=[go.Candlestick(
            # x=[f'[{i[:4]}/{i[4:6]}/{i[6:8]}]' for i in stock_df['date']],
            x=stock_df['date'],
            open=stock_df['open'], high=stock_df['high'], low=stock_df['low'], close=stock_df['close'],
            text=[f'거래량: {i:,}' for i in stock_df['volume']],
            increasing_line_color= 'red', decreasing_line_color= 'blue')]
    )
    candle_chart.update_layout(
        xaxis_rangeslider_visible=True,
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
    
    init_balance = 100_000_000    # TODO: 인자로 받아서 처리
    # PV chart
    df_pv = log_df.loc[:, ['epochs', 'pv', 'loss']]
    df_pv = df_pv.astype('float')
    pv_chart = px.line(df_pv, x='epochs', y='pv')
    pv_chart.add_hline(y=init_balance, line_width=1, line_color="red")
    pv_chart.update_layout(
        font={'size':10},
        margin=dict(t=20, b=20, l=10, r=10),
        height=400,
        paper_bgcolor="#fff", plot_bgcolor="#fff"
    )
    pv_chart.update_xaxes(showline=True, linewidth=2, linecolor='Lightgray', mirror=True)
    pv_chart.update_yaxes(range=[init_balance*0.5, init_balance*2], 
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
    
    # Create Layout ----------------------------------------
    train_dash_layout = dbc.Container([
        # dbc.Row(dbc.Col(html.H1('삼성전자 강화학습 결과', 
        #                         className='text-center text-primary mb-2'))),
        
        # dbc.Row(dbc.Col(html.Div(
        #     f"{params['stock_code']} #학습기간: {params['start_date']} ~ {params['end_date']} #강화학습: {params['rl_method']} #신경망: {params['net']} #learning rate: {params['lr']} #discount factor: {params['discount_factor']}",
        #     className='mb-4'), width={'size':12, 'offset':1})),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card([
                            dbc.CardBody([
                                html.H5('종목별 강화학습 결과', className='card-title mb-3'),
                                html.H6('삼성전자', className="card-subtitle mb-2"),
                                html.P(['- 시작일: 2020-01-01', html.Br(), 
                                        '- 종료일: 2020-09-30', html.Br(),
                                        '- 자본금: 100,000,000', html.Br(),
                                        '- 알고리즘: A2C, LSTM',
                                        ]),
                                html.Br(),
                                dbc.Row(
                                    [
                                        dbc.Label(["강화학습", html.Br(), "알고리즘"], html_for="choose_rl_method", width=4),
                                        dbc.Col(
                                            dbc.RadioItems(
                                                id="choose_rl_method",
                                                options=[
                                                    {'label':x, 'value':x}
                                                    for x in rl_list
                                                ],
                                                value = ['a2c'],
                                            ),
                                            width=8,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Label(["신경망", html.Br(), "알고리즘"], html_for="choose_net", width=4),
                                        dbc.Col(
                                            dbc.RadioItems(
                                                id="choose_net",
                                                options=[
                                                    {'label':x, 'value':x}
                                                    for x in net_list
                                                ],
                                                value = ['lstm'],
                                            ),
                                            width=8,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                            ]),
                        ]),
                    ], xs=12, sm=12, md=12, lg=3, xl=3,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            className="mb-2",
                            children=[
                            dbc.CardBody([
                                html.H5('평균 매매 비율', className='text-center text-info'),
                                dcc.Graph(id='pie_chart', figure=pie_chart),
                                # html.P('에포크를 반복하며 에이전트가 매수, 매도, 관망한 행동을 평균내어 비율화', 
                                #     className='card-text mb-5'),
                            ]),
                        ]),
                        dbc.Card(
                            className="mb-2",
                            children=[
                            dbc.CardBody([
                                html.H3('삼성전자 주가 차트', className='text-center text-info'),
                                dcc.Graph(id='candle_chart', figure=candle_chart),
                            ]),
                        ]),
                        dbc.Card(
                            className="mb-2",
                            children=[
                            dbc.CardBody([
                                html.H3('누적 학습에 따른 포트폴리오 가치 변화', className='text-center text-danger mt-5'),
                                dcc.Graph(id='pv_chart', figure=pv_chart),
                            ]),
                        ]),
                        dbc.Card(
                            className="mb-2",
                            children=[
                            dbc.CardBody([
                                html.H3('누적 학습에 따른 손실값 변화', className='text-center text-danger mt-5'),
                                dcc.Graph(id='loss_chart', figure=loss_chart),
                            ]),
                        ]),

                    ], xs=12, sm=12, md=12, lg=6, xl=6,
                ),
            ], justify="center",
        ),
    ], fluid=True)
    
    return train_dash_layout
    
layout = html.Div(
    id='train_dash_layout',
    children=[
        shared_dash_nav(),
        layout()
    ]
)