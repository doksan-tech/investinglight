import os
import time
import pandas as pd
from sqlalchemy import create_engine, text as sql_text
from flask import Flask, render_template, request
# from dash import Dash
# import dash_bootstrap_components as dbc     # 1.3.1


from rltrader.settings import BASE_DIR
main_path = os.path.abspath(os.path.join(BASE_DIR, 'rltrader/main.py'))

app = Flask(__name__)
engine = create_engine(os.getenv("DATABASE_URL"))



def reinforcement_learning_func():
    time.sleep(2)

@app.route('/')
def hello():
    return render_template("main.html")

@app.route('/register', methods=['post'])
def register():
    name = request.form["name"]
    stock_name = request.form["s_name"]
    rl_method = request.form["rl_method"]
    net = request.form["network"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    sdate = int(start_date)
    edate = int(end_date)

    ch_sname = "'"+stock_name+"'"
    query = "select distinct stockcode from stocks where stockname="+ch_sname+";"
    df_sname = pd.read_sql_query(con=engine.connect(), sql=sql_text(query))
    s_size = df_sname.size
    if s_size:
        var1 = df_sname['stockcode'][0]

    query = "select min(date) as s_date, max(date) as e_date from stocks"
    df_date = pd.read_sql_query(con=engine.connect(), sql=sql_text(query))
    db_sdate = df_date['s_date'][0]
    db_edate = df_date['e_date'][0]
    check = 0
    if sdate <= edate:
        if db_sdate <= edate and db_edate >= sdate:
            check = 1
            var2 = start_date
            var3 = end_date
    
    if s_size == 0 or check == 0:
        return render_template("choose_again.html")
    else:
        command = f"python {main_path} --name {name} --stock_code {var1} --rl_method {rl_method} --net {net} --start_date {var2} --end_date {var3}"
        os.system(command)
        # return render_template("result.html")
        return redirect('/chart')

if __name__ == '__main__':
    app.run(port=8050)