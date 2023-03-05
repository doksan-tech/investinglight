import pandas as pd
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from web.views.getdata import get_data, get_stock_price, get_unique_items


def register_callbacks(dash_app):
    
    df = get_data('train')
    
    @dash_app.callback(
        Output(component_id='pie_chart', component_property='figure'),
        Output(component_id='candle_chart', component_property='figure'),
        Output(component_id='pv_chart', component_property='figure'),
        Output(component_id='loss_chart', component_property='figure'),
        [Input(component_id='choose_train', component_property='value')]
    )
    def update_chart(selected):
        """selected: [종목코드, rl_method, net, lr, gamma, 시작일, 종료일, 초기 자본금]"""

        # pie chart
        df_selected = (df[(df['stock_code'] == selected[0]) &
                         (df['rl_method'] == selected[1]) &
                         (df['net'] == selected[2]) &
                         (df['lr'] == selected[3]) &
                         (df['discount_factor'] == selected[4]) &
                         (df['start_date'] == selected[5]) &
                         (df['end_date'] == selected[6]) &
                         (df['init_balance'] == selected[7])])
        df_trading = df_selected.loc[:, ['num_buy', 'num_sell', 'num_hold']]
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

        # candle chart
        stock_df = get_stock_price(selected[0], selected[5], selected[6])
        stock_df['date'] = stock_df['date'].apply(lambda x: str(x))
        candle_chart = go.Figure(
            data=[go.Candlestick(
                x=stock_df['date'],
                open=stock_df['open'], high=stock_df['high'], low=stock_df['low'], close=stock_df['close'],
                text=[f'거래량: {i:,}' for i in stock_df['volume']],
                increasing_line_color='red', decreasing_line_color='blue')]
        )
        candle_chart.update_layout(
            title={'text': stock_df['stockname'][0], 'x': 0.5, 'y': 0.98},
            title_font_color="#54B4D3",
            title_font_size=20,
            xaxis_rangeslider_visible=True,
            margin=dict(t=50, b=20, l=10, r=10),
            font={'size': 10},
        )

        # pv chart
        df_pv = df_selected.loc[:, ['epochs', 'pv', 'loss']]
        df_pv = df_pv.astype('float')
        pv_chart = px.line(df_pv, x='epochs', y='pv')
        pv_chart.add_hline(y=selected[7], line_width=1, line_color="red")
        pv_chart.update_layout(
            font={'size': 10},
            margin=dict(t=20, b=20, l=10, r=10),
            height=400,
            paper_bgcolor="#fff", plot_bgcolor="#fff"
        )
        pv_chart.update_xaxes(showline=True, linewidth=2, linecolor='Lightgray', mirror=True)
        pv_chart.update_yaxes(range=[selected[7] * 0.5, selected[7] * 2],
                              dtick=10_000_000, ticklabelstep=2,
                              gridcolor='Lightgray')

        # loss chart
        loss_chart = px.line(df_pv, x='epochs', y='loss')
        loss_chart.update_layout(
            font={'size': 10},
            margin=dict(t=20, b=20, l=10, r=10),
            height=400,
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        loss_chart.update_xaxes(showline=True, linewidth=2, linecolor='Lightgray', mirror=True)
        # loss_chart.update_yaxes(range=[0.5, 0.8], gridcolor='Lightgray')

        return pie_chart, candle_chart, pv_chart, loss_chart

