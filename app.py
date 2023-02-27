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

# 매수, 매도, 관망 평균 횟수 -----------------------------
df_trading = df.loc[:, ['num_buy', 'num_sell', 'num_hold']]
df_trading = df_trading.astype('int')
labels = ['매수','매도','관망']
values = [df_trading['num_buy'].mean(), df_trading['num_sell'].mean(), df_trading['num_hold'].mean()]
# Use `hole` to create a donut-like pie chart
pie_chart = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent', hole=.3)])
pie_chart.update_layout(
    showlegend=False,
    annotations=[dict(text='매매', x=0.5, y=0.5, font_size=20, showarrow=False)]
)

# 에포크 진행에 따른 포트폴리오 가치, loss 변화
df_pv = df.loc[:, ['epoch', 'pv', 'loss']]
df_pv = df_pv.astype('float')
pv_chart = px.line(df_pv, x='epoch', y='pv')
pv_chart.add_hline(y=int(params['balance']), line_width=1, line_color="red")
loss_chart = px.line(df_pv, x='epoch', y='loss')
pv_chart.update_layout(height=300)
loss_chart.update_layout(height=300)


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
candle_chart.update_layout(xaxis_rangeslider_visible=False)

#-----------------------------------------------------------------

application = flask.Flask(__name__)
dashapp = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server = application, url_base_pathname='/chart/')

@application.route('/')
def index():
    return 'index'

dashapp.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1('삼성전자 강화학습 결과', style={'textAlign': 'center'}))),
    dbc.Row([
        dbc.Col([
            html.H2("삼성전자 주가", style={'textAlign': 'center'}),
            dcc.Graph(figure=candle_chart),
        ], width=8),
        dbc.Col([
            html.H2("에이전트 평균 매매 횟수", style={'textAlign': 'center'}),
            dcc.Graph(figure=pie_chart),
        ], width=4),
    ], justify="center", align="middle"),
    dbc.Row([
        dbc.Col([
            html.H2("포트폴리오 가치 변화", style={'textAlign': 'center'}),
            dcc.Graph(figure=pv_chart),
        ], width=6),
        dbc.Col([
            html.H2("손실값 변화", style={'textAlign': 'center'}),
            dcc.Graph(figure=loss_chart),
        ], width=6),
    ], justify="center", align="loss_chart"),
])

if __name__ == "__main__":
    application.debug=True
    application.run()
