import os
import pandas as pd
from sqlalchemy import create_engine, text as sql_text
from flask import Flask, render_template, request
import time

engine = create_engine(os.getenv("DATABASE_URL"))
a = "삼성전자"
b = "'"+a+"'"
query = "select min(date) as s_date, max(date) as e_date from stocks"
df_market = pd.read_sql_query(con=engine.connect(), sql=sql_text(query))

print(df_market.size)
print(20222222>df_market['s_date'][0])