import time
import datetime
import numpy as np

# 날짜, 시간 관련 문자열 형식
FORMAT_DATE = "%Y%m%d"  # 4자리 연도, 2자리 월, 2자리 일
FORMAT_DATETIME = "%Y%m%d%H%M%S"    # 2자리 시, 2자리 분, 2자리 초

# datetime -> 사람이 보기 쉬운 문자열 형식의 시간값을 다룸
# datetime.date.today() -> datetime.date(2023, 2, 16)
# datetime.datetime.min.time() -> datetime.time(0, 0)
# datetime.datetime.combine(위 두 개) -> datetime.datetime(2023, 2, 16, 0, 0)
def get_today_str():
    today = datetime.datetime.combine(
        datetime.date.today(), datetime.datetime.min.time())
    today_str = today.strftime(FORMAT_DATE)    # '20230216'
    return today_str

# time.time() -> epoch time(=timestamp): UTC(GMT+0) 기준으로 1970년 1월 1일 0시 0분 0초부터의 경과 시간
# time -> Unix Timestamp로 불리는 숫자 형식의 시간값을 다룸
def get_time_str():
    return datetime.datetime.fromtimestamp(
        int(time.time())).strftime(FORMAT_DATETIME) # '20230216182912'

# TODO: # -10 <= x <= 10 ?? why 10 ??
def sigmoid(x):
    x = max(min(x, 10), -10)
    return 1. / (1. + np.exp(-x))
