import os, sys, json
import logging
import requests
from . import utils, settings, data_manager


def rltrader(mode='train', ver='v3', name='test', stock_code_list=['005930'], 
             rl_method='a2c', net='dnn', backend='pytorch',
             start_date=20200101, end_date=20201231, 
             lr=0.0001, discount_factor=0.9, balance=100_000_000):
    print('--------------main.py 시작--------------------')
    output_name = f'{mode}_{name}_{rl_method}_{net}'
    learning = mode in ['train', 'update']
    reuse_models = mode in ['test', 'update', 'predict']
    value_network_name = f'{name}_{rl_method}_{net}_value.mdl'
    policy_network_name = f'{name}_{rl_method}_{net}_policy.mdl'
    start_epsilon = 1 if mode in ['train', 'update'] else 0
    num_epoches = 1000 if mode in ['train', 'update'] else 1
    num_steps = 5 if net in ['lstm', 'cnn'] else 1

    # Backend 설정
    os.environ['RLTRADER_BACKEND'] = backend
    if backend == 'tensorflow':
        os.environ['KERAS_BACKEND'] = 'tensorflow'
    elif backend == 'plaidml':
        os.environ['KERAS_BACKEND'] = 'plaidml.keras.backend'

    # 출력 경로 생성 -> eg. BASE_DIR/output/train_20230219_dqn_lstm/
    # os.makedirs() -> 끝에 s가 붙는 것 주의!! 일치하는 디렉토리가 없어도 생성
    output_path = os.path.join(settings.BASE_DIR, 'output', output_name)
    if not os.path.isdir(output_path):  # 디렉토리 존재하면 True 반환
        os.makedirs(output_path)

    # 파라미터 기록 -> output/path/params.json 파일로 저장
    # vars(object) -> 내장함수. object 인수를 dict로 반환
    params = json.dumps({'mode':mode, 'ver':ver, 'name':name, 'stock_code':stock_code_list, 
                         'rl_method':rl_method, 'net':net, 'backend':backend,
                         'start_date':start_date, 'end_date':end_date, 
                         'lr':lr, 
                         'discount_factor':discount_factor, 'balance':balance})
    with open(os.path.join(output_path, 'params.json'), 'w') as f:
        f.write(params)

    # 모델 경로 준비
    # 모델 포멧은 TensorFlow는 h5, PyTorch는 pickle
    # BASE_DIR/models/20230216_dqn_rnn_value.mdl'
    # BASE_DIR/models/20230216_dqn_rnn_policy.mdl'
    value_network_path = os.path.join(settings.BASE_DIR, 'models', value_network_name)
    policy_network_path = os.path.join(settings.BASE_DIR, 'models', policy_network_name)

    # 로그 기록 설정
    # 로그 레벨: DEBUG < INFO < WARNING < ERROR < CRITICAL
    # https://docs.python.org/ko/3.8/howto/logging.html
    # BASE_DIR/output/train_20230219_dqn_lstm/train_20230219_dqn_lstm.log
    # TODO: StreamHandler - FileHandler 차이
    log_name = f'{mode}_{name}_{stock_code_list[0]}_{rl_method}_{net}.log'
    log_path = os.path.join(settings.BASE_DIR, 'output', log_name)  # 수정
    if os.path.exists(log_path):
        os.remove(log_path)
    logging.basicConfig(format='%(message)s', filemode='w')  # 화면에 출력할 내용
    logger = logging.getLogger(settings.LOGGER_NAME)  # logger 생성
    logger.setLevel(logging.DEBUG)  # 상세한 정보. 보통 문제를 진단할 때만 필요
    logger.propagate = False  # TODO: 모르겠음
    stream_handler = logging.StreamHandler(sys.stdout)  # 로그를 콘솔에 출력
    stream_handler.setLevel(logging.INFO)  # 예상대로 작동하는지에 대한 확인
    file_handler = logging.FileHandler(filename=log_path, encoding='utf-8')  # 로그를 파일에 출력
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    # logger.info(params)  # 파라미터 로그 파일에 기록

    # Backend 설정, 로그 설정을 먼저하고 RLTrader 모듈들을 이후에 임포트해야 함
    from .learners import ReinforcementLearner, DQNLearner, \
        PolicyGradientLearner, ActorCriticLearner, A2CLearner, A3CLearner

    # 학습기 클래스 인자 설정
    # A3C는 어러 종목의 학습을 병렬로 진행하기 때문에 리스트 자료형 필요
    common_params = {}
    list_stock_code = []
    list_chart_data = []
    list_training_data = []
    list_min_trading_price = []
    list_max_trading_price = []

    for stock_code in stock_code_list:
        # 차트 데이터(ohlcv), 학습 데이터(per 등) 준비
        chart_data, training_data = data_manager.load_data(
            stock_code, start_date, end_date, ver=ver)

        # assert : 뒤의 조건이 True가 아니면 AssertError를 발생
        # num_stepsdls : lstm, cnn -> 5, else -> 1
        # TODO: 차트 데이터의 개수가 num_steps보다 많아야 하지?? num_steps는 뭐지??
        assert len(chart_data) >= num_steps

        # 최소/최대 단일 매매 금액 설정
        min_trading_price = 100_000
        max_trading_price = 10_000_000

        # 공통 파라미터 설정
        common_params = {
            'rl_method': rl_method,
            'net': net,
            'num_steps': num_steps,
            'lr': lr,
            'balance': balance,
            'num_epoches': num_epoches,
            'discount_factor': discount_factor,
            'start_epsilon': start_epsilon,
            'output_path': output_path,
            'reuse_models': reuse_models,
            'mode':mode,
            'start_date':start_date, 
            'end_date':end_date,
        }

        # 강화학습 시작
        learner = None
        if rl_method != 'a3c':
            # dict.update() 기존 딕셔너리 데이터 업데이트
            common_params.update({'stock_code': stock_code,
                                    'chart_data': chart_data,
                                    'training_data': training_data,
                                    'min_trading_price': min_trading_price,
                                    'max_trading_price': max_trading_price})
            if rl_method == 'dqn':
                learner = DQNLearner(**{**common_params,
                                        'value_network_path': value_network_path})
            elif rl_method == 'pg':
                learner = PolicyGradientLearner(**{**common_params,
                                                    'policy_network_path': policy_network_path})
            elif rl_method == 'ac':
                learner = ActorCriticLearner(**{**common_params,
                                                'value_network_path': value_network_path,
                                                'policy_network_path': policy_network_path})
            elif rl_method == 'a2c':
                learner = A2CLearner(**{**common_params,
                                        'value_network_path': value_network_path,
                                        'policy_network_path': policy_network_path})
            elif rl_method == 'monkey':
                common_params['net'] = rl_method
                common_params['num_epoches'] = 10
                common_params['start_epsilon'] = 1
                learning = False
                learner = ReinforcementLearner(**common_params)
        else:
            list_stock_code.append(stock_code)
            list_chart_data.append(chart_data)
            list_training_data.append(training_data)
            list_min_trading_price.append(min_trading_price)
            list_max_trading_price.append(max_trading_price)

    # A3C는 인자를 리스트로 받음. 리스트 크기만큼 A2C 객체 생성
    if rl_method == 'a3c':
        learner = A3CLearner(**{
            **common_params,
            'list_stock_code': list_stock_code,
            'list_chart_data': list_chart_data,
            'list_training_data': list_training_data,
            'list_min_trading_price': list_min_trading_price,
            'list_max_trading_price': list_max_trading_price,
            'value_network_path': value_network_path,
            'policy_network_path': policy_network_path})

    # 학습기(learner) 객체가 있는지 확인
    assert learner is not None

    # train, test, update 모드 -> run() 실행 후 -> 학습한 모델 저장(update 제외)
    # predict 모드 -> predict() 실행
    if mode in ['train', 'test', 'update']:
        learner.run(learning=learning)
        if mode in ['train', 'update']:
            learner.save_models()
    elif mode == 'predict':
        learner.predict()

