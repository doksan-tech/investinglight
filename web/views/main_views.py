import requests
import os
from os import environ
import pandas as pd
from flask import Blueprint, url_for, request, redirect, render_template, jsonify
from sqlalchemy import create_engine, text as sql_text

from web.rltrader.main import rltrader

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def home():
    """매개변수 입력 화면"""
    return render_template("index.html")

@bp.route('/register', methods=['get','post'])
def register():
    if request.method == 'GET':
        engine = create_engine(os.environ.get("DATABASE_URL"))
        sql_1 = "SELECT * FROM stocks LIMIT 1;"
        sql_2 = "SELECT * FROM marketfeatures LIMIT 1;"
        sql_3 = "SELECT DISTINCT stockname, stockcode FROM stocks;"
        stockfeatures = pd.read_sql_query(con=engine.connect(), sql=sql_text(sql_1)).columns.to_list()
        marketfeatures = pd.read_sql_query(con=engine.connect(), sql=sql_text(sql_2)).columns.to_list()
        # stocks = pd.read_sql_query(con=engine.connect(), sql=sql_text(sql_3))
        features = stockfeatures[6:-2] + marketfeatures[1:] # date, stockcode, stockname 제외
        labels = [
            'PER',
            'PBR',
            'ROE',
            '전일 종가 대비 당일 시가 비율',
            '당일 고가 대비 종가 비율',
            '당일 저가 대비 종가 비율',
            '종가등락률',
            '전일 거래량 대비 당일 거래량 비율',
            '5일 이동평균 종가 대비 당일 종가',
            '5일 이동평균 거래량 대비 당일 거래량',
            '10일 이동평균 종가 대비 당일 종가',
            '10일 이동평균 거래량 대비 당일 거래량',
            '20일 이동평균 종가 대비 당일 종가',
            '20일 이동평균 거래량 대비 당일 거래량',
            '60일 이동평균 종가 대비 당일 종가',
            '60일 이동평균 거래량 대비 당일 거래량',
            '120일 이동평균 종가 대비 당일 종가',
            '120일 이동평균 거래량 대비 당일 거래량',
            '개인투자자 거래량',
            '개인투자자 전일 거래량과 당일 거래량 차이',
            '개인투자자 5일 이동평균 거래량',
            '개인투자자 10일 이동평균  거래량',
            '개인투자자 20일 이동평균  거래량',
            '개인투자자 60일 이동평균  거래량',
            '개인투자자 120일 이동평균 거래량',
            '기관투자자 거래량',
            '기관투자자 전일 거래량과 당일 거래량 차이',
            '기관투자자 5일 이동평균 거래량',
            '기관투자자 10일 이동평균 거래량',
            '기관투자자 20일 이동평균 거래량',
            '기관투자자 60일 이동평균 거래량',
            '기관투자자 120일 이동평균 거래량',
            '외국인투자자 거래량',
            '외국인투자자 전일 거래량과 당일 거래량 차이',
            '외국인투자자 5일 이동평균 거래량',
            '외국인투자자 10일 이동평균 거래량',
            '외국인투자자 20일 이동평균 거래량',
            '외국인투자자 60일 이동평균 거래량',
            '외국인투자자 120일 이동평균 거래량',
            '코스피 5일 이동평균 대비 당일 비율',
            '코스피 20일 이동평균 대비 당일 비율',
            '코스피 60일 이동평균 대비 당일 비율',
            '코스피 120일 이동평균 대비 당일 비율',
            '한국 국채 3년물 5일 이동평균 대비 당일 비율',
            '한국 국채 3년물 20일 이동평균 대비 당일 비율',
            '한국 국채 3년물 60일 이동평균 대비 당일 비율',
            '한국 국채 3년물 120일 이동평균 대비 당일 비율'
        ]
        print(len(features), len(labels))
        return render_template("register.html", features=features, labels=labels)
    elif request.method == 'POST':
        stock_code = ['000100']     # TODO: 수정
        engine = create_engine(environ.get("DATABASE_URL"))

        mode = request.form["mode"]
        stock_name = request.form["s_name"]    # TODO: 종목명을 입력하면 코드로 변환하는 코드 추가
        rl_method = request.form["rl_method"]
        net = request.form["network"]
        start_date = str(request.form["start_date"]).replace('-', '')
        end_date = str(request.form["end_date"]).replace('-', '')
        features = request.form.getlist('features')

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
        rltrader(mode=mode, stock_code_list=stock_code,
                rl_method=rl_method,  net=net,
                start_date=start_date, end_date=end_date,
                features=features)
        return render_template("result.html")