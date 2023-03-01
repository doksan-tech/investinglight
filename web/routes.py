"""Routes for parent Flask app."""
import os
import pandas as pd
from flask import current_app as app
from flask import render_template, request, redirect
from sqlalchemy import create_engine, text as sql_text

BASE_DIR = os.path.abspath(os.path.join(__file__, '../..'))

@app.route("/")
def home():
    """매개변수 입력 화면"""
    return render_template("main.html")

@app.route('/register', methods=['post'])
def register():
    
    main_path = os.path.abspath(os.path.join(BASE_DIR, 'rltrader/main.py'))
    engine = create_engine(os.getenv("DATABASE_URL"))
    
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
        return redirect('/learnchart')