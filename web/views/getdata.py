"""Prepare data for Plotly Dash"""
import os, sys, json
import pandas as pd
from sqlalchemy import create_engine, text as sql_text

# get project root directory
BASE_DIR = os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir, os.path.pardir))


def get_unique_items(df, column) -> list:
    return df[column].unique()


def log_to_df(file_list, columns):
    """강화학습, 테스트, 예측 로그 파일을 데이터프레임으로 반환"""
    log = []
    for file in file_list:
        with open(file, 'r') as f:
            lines = f.readlines()
        for line in lines[1:]:
            log.append(line.replace('\n', '').split(','))
    return pd.DataFrame(log, columns=columns)


def get_data(mode):
    """
    * 강화학습, 테스트, 예측 후 로그 데이터 가져오기
    * mode : train, test, predict
    """
    # output 폴더 내의 파일과 디렉토리 목록 가져오기
    path_dir = os.path.abspath(os.path.join(BASE_DIR, 'data/output/'))
    try:
        # 파일명만 변수에 담기
        df = pd.DataFrame()
        for file in os.listdir(path_dir):
            if mode in file:
                temp_df = pd.read_csv(path_dir + '/' + file, converters={'stock_code': lambda x: str(x)})
                df = pd.concat([df, temp_df], ignore_index=True)
        return df
    except:
        return None

def get_stock_price(stock_code, start_date, end_date):
    """주가 데이터 가져오기"""
    engine = create_engine(os.getenv("DATABASE_URL"))
    
    query = (f"SELECT stockname, stockcode, date, open, high, low, close, volume "
             f"FROM stocks "
             f"where stockcode='{stock_code}' AND "
                f"date>={start_date} AND "
                f"date<={end_date};")

    stock_df = pd.read_sql_query(con=engine.connect(), sql=sql_text(query))

    return stock_df
