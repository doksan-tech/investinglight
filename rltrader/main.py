import os
import sys
import logging
import argparse
import json
import utils, settings, data_manager


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['train', 'test', 'update', 'predict'], default='train')
    # RLTrader의 버전을 명시합니다.
    parser.add_argument('--ver', choices=['v1', 'v2', 'v3', 'v4'], default='v3')
    # 로그 등의 출력물을 저장할 폴더명과 모델 파일명에 사용되는 문자열. TODO: default 값은 날짜인데 종목명과 잘 맞지 않는다.
    parser.add_argument('--name', default=utils.get_time_str())
    # 강화학습의 환경이 될 주식의 종목 코드입니다. A3C의 경우 여러 개의 종목 코드를 입력합니다.
    parser.add_argument('--stock_code', nargs='+')
    # 강화학습 방식을 설정합니다. dqn, pg, ac, a2c, a3c 중에서 하나를 정합니다.
    parser.add_argument('--rl_method', choices=['dqn', 'pg', 'ac', 'a2c', 'a3c', 'monkey'])
    # 가치 신경망과 정책 신경망에서 사용할 신경망 유형을 선택합니다. dnn, lstm, cnn 중 에서 하나를 정합니다.
    parser.add_argument('--net', choices=['dnn', 'lstm', 'cnn', 'monkey'], default='dnn')
    # Keras의 백엔드로 사용할 프레임워크를 설정합니다. tensorflow와 plaidml을 선택할수있습니다
    parser.add_argument('--backend', choices=['pytorch', 'tensorflow', 'plaidml'], default='pytorch')
    # 차트 데이터 및 학습 데이터 시작 날짜
    parser.add_argument('--start_date', default='20200101')
    # 차트 데이터 및 학습 데이터 끝 날짜
    parser.add_argument('--end_date', default='20201231')
    parser.add_argument('--lr', type=float, default=0.0001)
    parser.add_argument('--discount_factor', type=float, default=0.9)
    parser.add_argument('--balance', type=int, default=100_000_000)
    args = parser.parse_args()

    # 학습기 파라미터 설정
    # 로그, 시각화 파일 등 출력 파일을 저장할 폴더 이름
    output_name = f'{args.mode}_{args.name}_{args.rl_method}_{args.net}'
    # boolean -> 강화학습 여부 지정. train, update 모드에서 학습 기능 활성화
    learning = args.mode in ['train', 'update']
    # boolean -> 신경망 모델 재사용 여부 지정. test, update, predict 모드에서 저장된 모델을 불러와 사용
    reuse_models = args.mode in ['test', 'update', 'predict']
    # 가치 신경망 모델을 저장할 파일명
    value_network_name = f'{args.name}_{args.rl_method}_{args.net}_value.mdl'
    # 정책 신경망 모델을 저장할 파일명
    policy_network_name = f'{args.name}_{args.rl_method}_{args.net}_policy.mdl'
    # 시작 탐험률
    start_epsilon = 1 if args.mode in ['train', 'update'] else 0
    # 수행할 에포크 수
    num_epoches = 10 if args.mode in ['train', 'update'] else 1
    # LSTM, CNN에서 사용할 step 크기
    num_steps = 5 if args.net in ['lstm', 'cnn'] else 1

    # Backend 설정
    # os.environ -> 운영체제의 환경변수에 접근.
    # args.backend로 받은 인수를 저장하고, tensorflow, plaidml에 따라 저장
    os.environ['RLTRADER_BACKEND'] = args.backend
    if args.backend == 'tensorflow':
        os.environ['KERAS_BACKEND'] = 'tensorflow'
    elif args.backend == 'plaidml':
        os.environ['KERAS_BACKEND'] = 'plaidml.keras.backend'

    # 출력 경로 생성 -> eg. BASE_DIR/output/train_20230219_dqn_lstm/
    # os.makedirs() -> 끝에 s가 붙는 것 주의!! 일치하는 디렉토리가 없어도 생성
    output_path = os.path.join(settings.BASE_DIR, 'output', output_name)
    if not os.path.isdir(output_path):  # 디렉토리 존재하면 True 반환
        os.makedirs(output_path)

    # 파라미터 기록 -> output/path/params.json 파일로 저장
    # vars(object) -> 내장함수. object 인수를 dict로 반환
    params = json.dumps(vars(args))
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
    log_path = os.path.join(settings.BASE_DIR, 'output', 'epoch.log')  # 수정
    if os.path.exists(log_path):
        os.remove(log_path)
    logging.basicConfig(format='%(message)s')  # 화면에 출력할 내용
    logger = logging.getLogger(settings.LOGGER_NAME)  # logger 생성
    logger.setLevel(logging.DEBUG)  # 상세한 정보. 보통 문제를 진단할 때만 필요
    logger.propagate = False  # TODO: 모르겠음
    stream_handler = logging.StreamHandler(sys.stdout)  # 로그를 콘솔에 출력
    stream_handler.setLevel(logging.INFO)  # 예상대로 작동하는지에 대한 확인
    file_handler = logging.FileHandler(filename=log_path, encoding='utf-8')  # 로그를 파일에 출력
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.info(params)  # 파라미터 로그 파일에 기록

    # Backend 설정, 로그 설정을 먼저하고 RLTrader 모듈들을 이후에 임포트해야 함
    from learners import ReinforcementLearner, DQNLearner, \
        PolicyGradientLearner, ActorCriticLearner, A2CLearner, A3CLearner

    # 학습기 클래스 인자 설정
    # A3C는 어러 종목의 학습을 병렬로 진행하기 때문에 리스트 자료형 필요
    common_params = {}
    list_stock_code = []
    list_chart_data = []
    list_training_data = []
    list_min_trading_price = []
    list_max_trading_price = []

    for stock_code in args.stock_code:
        # 차트 데이터(ohlcv), 학습 데이터(per 등) 준비
        chart_data, training_data = data_manager.load_data(
            stock_code, args.start_date, args.end_date, ver=args.ver)

        # assert : 뒤의 조건이 True가 아니면 AssertError를 발생
        # num_stepsdls : lstm, cnn -> 5, else -> 1
        # TODO: 차트 데이터의 개수가 num_steps보다 많아야 하지?? num_steps는 뭐지??
        assert len(chart_data) >= num_steps

        # 최소/최대 단일 매매 금액 설정
        min_trading_price = 100_000
        max_trading_price = 10_000_000

        # 공통 파라미터 설정
        common_params = {
            'rl_method': args.rl_method,
            'net': args.net,
            'num_steps': num_steps,
            'lr': args.lr,
            'balance': args.balance,
            'num_epoches': num_epoches,
            'discount_factor': args.discount_factor,
            'start_epsilon': start_epsilon,
            'output_path': output_path,
            'reuse_models': reuse_models
        }

        # 강화학습 시작
        learner = None
        if args.rl_method != 'a3c':
            # dict.update() 기존 딕셔너리 데이터 업데이트
            common_params.update({'stock_code': stock_code,
                                  'chart_data': chart_data,
                                  'training_data': training_data,
                                  'min_trading_price': min_trading_price,
                                  'max_trading_price': max_trading_price})
            if args.rl_method == 'dqn':
                learner = DQNLearner(**{**common_params,
                                        'value_network_path': value_network_path})
            elif args.rl_method == 'pg':
                learner = PolicyGradientLearner(**{**common_params,
                                                   'policy_network_path': policy_network_path})
            elif args.rl_method == 'ac':
                learner = ActorCriticLearner(**{**common_params,
                                                'value_network_path': value_network_path,
                                                'policy_network_path': policy_network_path})
            elif args.rl_method == 'a2c':
                learner = A2CLearner(**{**common_params,
                                        'value_network_path': value_network_path,
                                        'policy_network_path': policy_network_path})
            elif args.rl_method == 'monkey':
                common_params['net'] = args.rl_method
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
    if args.rl_method == 'a3c':
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
    if args.mode in ['train', 'test', 'update']:
        learner.run(learning=learning)
        if args.mode in ['train', 'update']:
            learner.save_models()
    elif args.mode == 'predict':
        learner.predict()

