import os
import locale
import platform

# 로거 이름
LOGGER_NAME = 'rltrader'

# 경로 설정: BASE_DIR -> 프로젝트 최상위 경로
# os.environ 설명 -> https://www.geeksforgeeks.org/python-os-environ-object/
# BASE_DIR = os.environ.get('RLTRADER_BASE',
#     os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir, os.path.pardir)))
# -> RLTRADER_BASE 환경 변수가 존재하면 그 값을 사용하고, 없으면 settings 모듈 기준으로 세 번째 상위 폴더 선택하라.
BASE_DIR = os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir, os.path.pardir))


# 리눅스와 맥에서 한국어 지원 위해 로케일 설정 -> 한글 시간 사용하기(%Y년 %m월 %d일)
# 로케일 설정(https://docs.python.org/ko/3/library/locale.html)
if 'Linux' in platform.system() or 'Darwin' in platform.system():
    locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
elif 'Windows' in platform.system():
    locale.setlocale(locale.LC_ALL, '')
