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
    log_path = os.path.abspath(os.path.join(BASE_DIR, 'output'))
    output_list = os.listdir(log_path)
    
    # 파일명만 변수에 담기
    file_list = []
    for item in output_list:
        path = log_path + '/' + item
        if os.path.isfile(path):
            file_list.append(path)
    
    if mode == 'train':
        train_list = [ i for i in file_list if 'train' in i]
        train_columns = ['mode','stockcode','epochs','epsilon','num_exploration','num_buy','num_sell','num_hold','num_stocks','pv','loss','rl_method','net','lr','discount_factor','start_date','end_date','init_balance']
        train_df = log_to_df(train_list, train_columns)
        return train_df
    elif mode == 'test':
        test_list = [ i for i in file_list if 'test' in i]
        test_columns = ['mode','stockcode','epochs','epsilon','num_exploration','num_buy','num_sell','num_hold','num_stocks','pv','loss','rl_method','net','lr','discount_factor','start_date','end_date','init_balance']
        test_df = log_to_df(test_list, test_columns)
        return test_df
    elif mode == 'predict':
        predict_list = [ i for i in file_list if 'predict' in i]
        predict_columns = ['mode','stockcode','date','action','action_value']
        predict_df = log_to_df(predict_list, predict_columns)
        return predict_df
    
def get_stock_price(stockcode, start_date, end_date):
    """주가 데이터 가져오기"""
    engine = create_engine(os.getenv("DATABASE_URL"))
    
    query = (f"SELECT stockname, stockcode, date, open, high, low, close, volume "
            f"FROM stocks "
            f"where stockcode='{stockcode}' AND "
                f"date>={start_date} AND "
                f"date<={end_date};")

    stock_df = pd.read_sql_query(con=engine.connect(), sql=sql_text(query))

    return stock_df
