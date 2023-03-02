import requests
from os import environ
import pandas as pd
from flask import Blueprint, url_for, request, redirect, render_template, jsonify
from sqlalchemy import create_engine, text as sql_text

from web.rltrader.main import rltrader

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/hello')
def hello():
    return 'Hello bp'

@bp.route('/')
def home():
    """매개변수 입력 화면"""
    return render_template("index.html")

@bp.route('/register', methods=['get','post'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    elif request.method == 'POST':
        stock_code = ['005930']     # TODO: 수정
        engine = create_engine(environ.get("DATABASE_URL"))
        
        name = request.form["name"]
        mode = request.form["mode"]
        stock_name = request.form["s_name"]
        rl_method = request.form["rl_method"]
        net = request.form["network"]
        start_date = str(request.form["start_date"]).replace('-', '')
        end_date = str(request.form["end_date"]).replace('-', '')
        print(start_date)
        # ch_sname = "'"+stock_name+"'"
        # query = "select distinct stockcode from stocks where stockname="+ch_sname+";"
        # df_sname = pd.read_sql_query(con=engine.connect(), sql=sql_text(query))
        # s_size = df_sname.size
        # if s_size:
        #     stock_code.append(df_sname['stockcode'][0])

        # query = "select min(date) as s_date, max(date) as e_date from stocks"
        # df_date = pd.read_sql_query(con=engine.connect(), sql=sql_text(query))
        # db_start_date = str(df_date['s_date'][0])
        # db_end_date = str(df_date['e_date'][0])
        # check = 0
        # if start_date <= end_date:
        #     if db_start_date <= end_date and db_end_date >= start_date:
        #         check = 1
        #         var2 = start_date
        #         var3 = end_date
        
        # if s_size == 0 or check == 0:
        #     return render_template("choose_again.html")
        # else:
        rltrader(name=name, mode=mode, stock_code_list=stock_code,
                rl_method=rl_method,  net=net,
                start_date=start_date, end_date=end_date,
                )
        return 'Training Done'