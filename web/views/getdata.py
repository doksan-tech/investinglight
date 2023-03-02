"""Prepare data for Plotly Dash"""
import os, sys, json
import pandas as pd
from sqlalchemy import create_engine, text as sql_text

# get project root directory
BASE_DIR = os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir))

# connect db
engine = create_engine(os.getenv("DATABASE_URL"))

def getdata():
    
    log_path = os.path.abspath(os.path.join(BASE_DIR, 'output', logfile))
    
    file_list = os.listdir(log_path)
    
    print(file_list)
    sys.exit(0)
    
    with open(log_path, 'r') as f:
        lines = f.readlines()
    
    # {'mode': 'train', 'ver': 'v3', 'name': '0227_005930', 'stock_code': ['005930'], 
    # 'rl_method': 'a2c', 'net': 'lstm', 'backend': 'pytorch', 
    # 'start_date': '20200101', 'end_date': '20201231', 
    # 'lr': 0.0001, 'discount_factor': 0.9, 'balance': 100000000}
    params = lines[0]
    params = json.loads(params)

    # [005930] RL:a2c NET:lstm LR:0.0001 DF:0.9
    learner = lines[1]
    print(learner)
    # [005930] Elapsed Time:17.3947 Max PV:149,374,384 #Win:10
    result = lines[-1]
    
    columns = lines[2].replace('\n', '').split(',')
    epoch = []
    for line in lines[3:-1]:
        epoch.append(line.replace('\n', '').split(','))
    log_df = pd.DataFrame(epoch, columns=columns)
    
    query = (f"SELECT stockname, stockcode, date, open, high, low, close, volume "
             f"FROM stocks "
             f"where stockcode={params['stock_code'][0]} AND "
                f"date>={params['start_date']} AND "
                f"date<={params['end_date']}")
    stock_df = pd.read_sql_query(con=engine.connect(), sql=sql_text(query))
    
    return stock_df, log_df, params, learner, result
