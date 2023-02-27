# __init__.py 파일은 해당 디렉터리가 패키지의 일부임을 알려주는 역할을 한다

import os

# main.py의 "os.environ['RLTRADER_BACKEND'] = args.backend"에서 입력된 값
# 디폴트는 pytorch
if os.environ.get('RLTRADER_BACKEND', 'pytorch') == 'pytorch':
    from networks.networks_pytorch import Network, DNN, LSTMNetwork, CNN
else:
    from networks.networks_keras import Network, DNN, LSTMNetwork, CNN

# __all__ 리스트에 공개하려는 클래스를 명시해야 networks 패키지에서 이 클래스들을 임포트할 수 있다.
__all__ = [
    'Network', 'DNN', 'LSTMNetwork', 'CNN'
]