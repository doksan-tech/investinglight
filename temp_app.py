import os
import json
import flask
import pandas as pd
from dash import Dash, html, dcc
import plotly.express as px                 # 5.13.0
import plotly.graph_objects as go
import dash_bootstrap_components as dbc     # 1.3.1
from rltrader.settings import BASE_DIR


# 로그 분석 ---------------------
log_path = os.path.abspath(os.path.join(BASE_DIR, 'output/epoch.log'))

with open(log_path, 'r') as f:
    lines = f.readlines()
params = lines[0]
learner = lines[1]
result = lines[-1]
columns = lines[2].replace('\n', '').split(',')
epoch = []
for line in lines[3:-1]:
    epoch.append(line.replace('\n', '').split(','))

df = pd.DataFrame(epoch, columns=columns)
# print(df)
params = json.loads(params)
# print(f"[{params['stock_code'][0]}] {params['start_date']} ~ {params['end_date']}")
# print(f"learning rate: {params['lr']}, discount factor: {params['discount_factor']}")

# 매수, 매도, 관망 평균 횟수 차트 -----------------------------
df_trading = df.loc[:, ['num_buy', 'num_sell', 'num_hold']]
df_trading = df_trading.astype('int')
labels = ['매수','매도','관망']
values = [df_trading['num_buy'].mean(), df_trading['num_sell'].mean(), df_trading['num_hold'].mean()]
# Use `hole` to create a donut-like pie chart
pie_chart = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent', hole=.3)])
pie_chart.update_layout(
    showlegend=False,
    annotations=[dict(text='매매', x=0.5, y=0.5, font_size=15, showarrow=False)],
    # title={'text':'평균 매매 비율', 'x':0.5, 'y':0.9},
    title_font_color="red",
    title_font_size=25,
    font={'size':13},
    height=300,
    margin_autoexpand=False,
    margin=dict(t=20, b=20, l=10, r=10)
)

# 에포크 진행에 따른 포트폴리오 가치, loss 변화 차트 ------------------
df_pv = df.loc[:, ['epoch', 'pv', 'loss']]
df_pv = df_pv.astype('float')
pv_chart = px.line(df_pv, x='epoch', y='pv')
pv_chart.add_hline(y=int(params['balance']), line_width=1, line_color="red")
pv_chart.update_layout(
    # title={'title':'포트폴리오 가치 변화', 'x':0.5, 'y':0.9},
    # title_font_color="red",
    # title_font_size=25,
    font={'size':10},
    margin=dict(t=20, b=20, l=10, r=10),
    height=400,
    paper_bgcolor="#fff", plot_bgcolor="#fff"
    )
pv_chart.update_xaxes(showline=True, linewidth=2, linecolor='Lightgray', mirror=True)
pv_chart.update_yaxes(range=[int(params['balance'])*0.5, int(params['balance'])*2], 
                      dtick=10_000_000, ticklabelstep=2,
                      gridcolor='Lightgray') # 시작값 작동 안 함

loss_chart = px.line(df_pv, x='epoch', y='loss')
loss_chart.update_layout(
    # title={'title':'손실값 변화', 'x':0.5, 'y':0.9},
    # title_font_color="red",
    # title_font_size=25,
    font={'size':10},
    margin=dict(t=20, b=20, l=10, r=10),
    height=400,
    paper_bgcolor="#fff", plot_bgcolor="#fff")
loss_chart.update_xaxes(showline=True, linewidth=2, linecolor='Lightgray', mirror=True)
loss_chart.update_yaxes(range=[0.5, 0.8], gridcolor='Lightgray')


# 주가 차트 그리기 ----------------------------
start_day = int(params['start_date'])
end_day = int(params['end_date'])

df = pd.read_csv('data/v3/005930_삼성전자.csv', usecols=['date', 'open', 'high', 'low', 'close', 'volume'])
df = df[ (df['date'] > start_day) & (df['date'] < end_day) ]
df = df.reset_index(drop=True)
df['date'] = df['date'].apply(lambda x: str(x))
candle_chart = go.Figure(data=[go.Candlestick(x=[f'[{i[:4]}/{i[4:6]}/{i[6:8]}]' for i in df['date']],
        open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        text=[f'거래량: {i:,}' for i in df['volume']],
        increasing_line_color= 'red', decreasing_line_color= 'blue',
)])
candle_chart.update_layout(
    xaxis_rangeslider_visible=False,
    # title={'text':'삼성전자 주가 차트', 'x':0.5, 'y':0.9},
    # title_font_color="red",
    # title_font_size=25,
    margin=dict(t=20, b=20, l=10, r=10),
    font={'size':10},
)

# 레이아웃 -----------------------------------------------------------------

application = flask.Flask(__name__)
dashapp = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], 
               meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}], 
               server = application, url_base_pathname='/chart/')

@application.route('/')
def index():
    return 'index'

dashapp.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1('삼성전자 강화학습 결과', 
                            className='text-center text-primary mb-2'))),
    dbc.Row(dbc.Col(html.Div(
        f"{params['stock_code']} #학습기간: {params['start_date']} ~ {params['end_date']} #강화학습: {params['rl_method']} #신경망: {params['net']} #learning rate: {params['lr']} #discount factor: {params['discount_factor']}",
        className='mb-4'), width={'size':12, 'offset':1})),
    dbc.Row([
        dbc.Col([
            html.H3('삼성전자 주가 차트', className='text-center text-danger mb-5'),
            dcc.Graph(figure=candle_chart),
        ], #width={'size':8}
           xs=12, sm=12, md=12, lg=8, xl=8 ),  # 작은 화면에서는 12칸 모두 사용하고, 큰 화면에서는 8칸 사용
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H3('평균 매매 비율', className='text-center text-danger'),
                    dcc.Graph(figure=pie_chart),
                    html.P('에포크를 반복하며 매수, 매도, 관망한 평균 비율', className='card-text mb-5'),
                ]),
            ]),
        ], #width={'size':3} 
           xs=12, sm=12, md=12, lg=4, xl=4 ),
    ], justify="around", align="start"),
    dbc.Row([
        dbc.Col([
            html.H3('누적 학습에 따른 포트폴리오 가치 변화', className='text-center text-danger mt-5'),
            dcc.Graph(figure=pv_chart),
        ], #width={'size':6}
           xs=12, sm=12, md=12, lg=6, xl=6),
        dbc.Col([
            html.H3('누적 학습에 따른 손실값 변화', className='text-center text-danger mt-5'),
            dcc.Graph(figure=loss_chart),
        ], #width={'size':6}
           xs=12, sm=12, md=12, lg=6, xl=6),
    ], justify="around", align="loss_chart"),
], fluid=True)

if __name__ == "__main__":
    application.debug=True
    application.run()
