"""Routes for parent Flask app."""
import os, sys
import pandas as pd
from flask import current_app as app
from flask import render_template, request, redirect, jsonify
from sqlalchemy import create_engine, text as sql_text

from rltrader.main import rltrader

BASE_DIR = os.path.abspath(os.path.join(__file__, '../..'))

@app.route("/")
def home():
    """매개변수 입력 화면"""
    return render_template("main.html")

@app.route('/register', methods=['post'])
def register():
    stock_code = []
    main_path = os.path.abspath(os.path.join(BASE_DIR, 'rltrader/main.py'))
    engine = create_engine(os.getenv("DATABASE_URL"))
    
    name = request.form["name"]
    stock_name = request.form["s_name"]
    rl_method = request.form["rl_method"]
    net = request.form["network"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]

    ch_sname = "'"+stock_name+"'"
    query = "select distinct stockcode from stocks where stockname="+ch_sname+";"
    df_sname = pd.read_sql_query(con=engine.connect(), sql=sql_text(query))
    s_size = df_sname.size
    if s_size:
        stock_code.append(df_sname['stockcode'][0])

    query = "select min(date) as s_date, max(date) as e_date from stocks"
    df_date = pd.read_sql_query(con=engine.connect(), sql=sql_text(query))
    db_start_date = str(df_date['s_date'][0])
    db_end_date = str(df_date['e_date'][0])
    check = 0
    if start_date <= end_date:
        if db_start_date <= end_date and db_end_date >= start_date:
            check = 1
            var2 = start_date
            var3 = end_date
    
    if s_size == 0 or check == 0:
        return render_template("choose_again.html")
    else:
        rltrader(name=name, stock_code_list=stock_code,
                 rl_method=rl_method,  net=net,
                 start_date=start_date, end_date=end_date,
                 )
        return redirect('/learnchart')