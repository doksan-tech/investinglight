import pandas as pd
import os
import sys
import pymysql
from sqlalchemy import create_engine

data_path = 'data/v3'
file_list = os.listdir(data_path)

BASE_DIR = os.path.abspath(__file__)

i = 0
for file in file_list:
    if file == 'marketfeatures.csv':
        file_path = os.path.join(data_path, file)
        df = pd.read_csv(file_path)
    
        engine = create_engine(os.getenv("DATABASE_URL"))
        df.to_sql(name="marketfeatures", con=engine, if_exists="append", index=False)

    else:
        file_path = os.path.join(data_path, file)
        df = pd.read_csv(file_path)
        df['stockcode'] = str(file.split('_')[0])
        df['stockname'] = str(file.split('_')[1].split('.')[0])
    
        engine = create_engine(os.getenv("DATABASE_URL"))
        df.to_sql(name="stocks", con=engine, if_exists="append", index=False)

    print(f'{i} - {file_path}')
    i += 1