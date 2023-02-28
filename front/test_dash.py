import dash
import dash_bootstrap_components as dbc
import os
import pandas as pd
from sqlalchemy import create_engine, text as sql_text
from flask import Flask, render_template, request

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
engine = create_engine(os.getenv("DATABASE_URL"))
query = 'select * from marketfeatures;'
query2 = 'select * from stocks;'
df_market = pd.read_sql_query(con=engine.connect(), sql=sql_text(query))
df_stock = pd.read_sql_query(con=engine.connect(), sql=sql_text(query2))
market_col = list(df_market.columns)
stock_col = list(df_stock.columns)
all_col = market_col + stock_col

@app.route('/')
def hello():
    return render_template("main.html", data=all_col)

@app.route('/register', methods=['post'])
def register():
    learn_col = []
    for col in all_col:
        temp = request.form.get(col)
        if temp:
            learn_col.append(col)
    if len(learn_col):
        return render_template("result.html", data=learn_col)
    else:
        return render_template("choose_again.html")

if __name__ == "__main__":
    app.run_server()