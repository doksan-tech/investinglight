# 투자 행동 수행 및 투자금과 보유 주식 관리

import numpy as np
import utils


class Agent:
    # 에이전트 상태가 구성하는 값 개수 -> 주식_보유_비율, 현재_손익, 평균_매수_단가_대비_등락률
    # 주식 보유 비율: ratio_hold = 보유주식수 * 현재가 / 포트폴리오 가치
    # 현재 손익: profitloss =  포트폴리오_가치 / 초기_자본금 - 1
    # 평균 매수 단가 대비 등락률: 주가 / 평균_매수_단가 - 1
    STATE_DIM = 3

    # 매매 수수료 및 세금
    TRADING_CHARGE = 0.00015  # 거래 수수료 0.015%
    # TRADING_CHARGE = 0.00011  # 거래 수수료 0.011%
    # TRADING_CHARGE = 0  # 거래 수수료 미적용
    TRADING_TAX = 0.0025  # 거래세 0.25%
    # TRADING_TAX = 0  # 거래세 미적용

    # 행동
    ACTION_BUY = 0  # 매수
    ACTION_SELL = 1  # 매도
    ACTION_HOLD = 2  # 관망
    # 정책 신경망이 확률을 구할 행동들을 저장하는 리스트 변수
    ACTIONS = [ACTION_BUY, ACTION_SELL, ACTION_HOLD]
    NUM_ACTIONS = len(ACTIONS)  # 인공 신경망에서 고려할 출력값의 개수

    def __init__(self, environment, initial_balance, min_trading_price, max_trading_price):
        # 현재 주식 가격을 가져오기 위해 환경 참조
        self.environment = environment
        self.initial_balance = initial_balance  # 초기 자본금

        # 최소 단일 매매 금액, 최대 단일 매매 금액
        self.min_trading_price = min_trading_price
        self.max_trading_price = max_trading_price

        # Agent 클래스의 속성
        self.balance = initial_balance  # 현재 현금 잔고
        self.num_stocks = 0  # 보유 주식 수
        # 포트폴리오 가치: 현금_잔고 + 보유_주식_수 * 현재_주식_가격
        self.portfolio_value = 0
        self.num_buy = 0  # 매수 횟수
        self.num_sell = 0  # 매도 횟수
        self.num_hold = 0  # 관망 횟수

        # Agent 클래스의 상태 -> 신경망에 입력으로 들어가는 샘플에 포함됨
        self.ratio_hold = 0  # 주식 보유 비율
        self.profitloss = 0  # 현재 손익
        self.avg_buy_price = 0  # 주당 매수 단가

    def reset(self):
        """
        에이전트 상태 초기화
        """

        self.balance = self.initial_balance
        self.num_stocks = 0
        self.portfolio_value = self.initial_balance
        self.num_buy = 0
        self.num_sell = 0
        self.num_hold = 0
        self.ratio_hold = 0
        self.profitloss = 0
        self.avg_buy_price = 0

    def set_balance(self, balance):
        """
        초기 자본금 설정
        :param balance: 초기 자본금
        """

        self.initial_balance = balance

    def get_states(self):
        """
        에이전트 상태 가져오기

        * ratio_hold: 주식_보유_비율 = 보유주식수 * 현재_주가 / 포트폴리오_가치
        *  -> 주식 보유 비율이 높으면 매도의 관점에서, 낮으면 매수 관점에서 투자에 임하게 됨
        * profitloss: 손익률 = 포트폴리오_가치 / 초기_자본금 - 1
        * 평균_매수_단가_대비_등락률: 주가 / 평균_매수_단가 - 1
        :return: 주식_보유_비율, 현재_손익, 평균_매수_단가_대비_등락률
        """

        self.ratio_hold = (self.num_stocks
                           * self.environment.get_price()
                           / self.portfolio_value)
        return (
            self.ratio_hold,
            self.profitloss,
            ((self.environment.get_price() / self.avg_buy_price) - 1
                if self.avg_buy_price > 0 else 0)
        )

    def decide_action(self, pred_value, pred_policy, epsilon):
        """
        탐험 또는 정책 신경망에 의한 행동 결정
        :param pred_value:
        :param pred_policy: 정책 신경망의 출력
        :param epsilon: (0, 1] 랜덤 값이 엡실론보다 작으면 무작위로 행동 결정
        :return: action, confidence, exploration
        """

        # TODO: confidence 변수는 뭘까?
        confidence = 0.

        pred = pred_policy
        # DQN은 pred_policy가 None -> pred_value로 행동 결정
        if pred is None:
            pred = pred_value

        if pred is None:
            # 예측 값이 없을 경우 탐험
            epsilon = 1
        else:
            # 값이 모두 같은 경우 탐험
            maxpred = np.max(pred)
            if (pred == maxpred).all():  # TODO: 특이한 코드다. np.all(pred == maxpred)와 같을까?
                epsilon = 1

            # if pred_policy is not None:
            #     if np.max(pred_policy) - np.min(pred_policy) < 0.05:
            #         epsilon = 1

        # 탐험 결정
        if np.random.rand() < epsilon:  # 무작위 숫자가 엡실론보다 작으면 -> 무작위 행동
            exploration = True
            # 행동 랜덤 선택. 0 ~ 행동개수-1
            action = np.random.randint(self.NUM_ACTIONS)
        else:
            exploration = False
            action = np.argmax(pred)

        confidence = .5
        if pred_policy is not None:
            confidence = pred[action]   # 정책 신경망 -> 소프트맥스 확률값
        elif pred_value is not None:
            confidence = utils.sigmoid(pred[action])

        return action, confidence, exploration

    def validate_action(self, action):
        """
        * 행동의 유효성 판단. 신용 매수나 공매도 고려하지 않음.
        * 수수료를 포함해 적어도 한 주를 살 수 있는 잔고가 있어야 매수 가능
        * 보유한 주식이 있어야 매도 가능
        :param action: 매수, 매도
        :return: 매수[도]가 가능하면 True, 불가능하면 Flase 반환
        """

        if action == Agent.ACTION_BUY:
            # 적어도 1주를 살 수 있는지 확인
            if self.balance < self.environment.get_price() * (1 + self.TRADING_CHARGE):
                return False
        elif action == Agent.ACTION_SELL:
            # 주식 잔고가 있는지 확인
            if self.num_stocks <= 0:
                return False
        return True

    def decide_trading_unit(self, confidence):
        """
        결정한 행동의 신뢰(confidence)에 따라 매수 또는 매도할 주식 수 결정
        :param confidence: 매매 강도(confidenct를 곱한 액수 만큼 추가 매수) pred[action] or [0 ~ 1]
        :return: min_trading_price(최소 단일 매매 금액) or 매매 주식 수(거래금액 / 매매가)
        """

        # confidence가 없으면 최소 단일 매매 금액 반환
        # TODO: confidence가 NaN인 경우가 있을 수 있을까? act()에서 에러 발생할텐데
        if np.isnan(confidence):
            return self.min_trading_price
        # 추가 매매 금액 계산 -> (0 ~ (최대매매금액-최소매매금액))
        added_trading_price = \
            max(    # confidence < 0 일 경우 최소매매금액보다 작지 않도록
                min(    # confidence > 1 일 경우 최대매매금액을 넘어서지 못하도록
                    int(confidence * (self.max_trading_price - self.min_trading_price)),
                    self.max_trading_price - self.min_trading_price)
                , 0
            )
        # 매매 금액 = 최소 매매 금액 + 추가 매매 금액
        trading_price = self.min_trading_price + added_trading_price
        # 매매 수량 = 매매 금액 / 매매가. max( ... , 1) -> 최소 1주 거래
        return max(int(trading_price / self.environment.get_price()), 1)

    def act(self, action, confidence):
        """
        * 매수(0) or 매도(1) or 관망(2) 수행
        * 포트폴리오 가치 갱신
        :param action: 매수(0) or 매도(1)
        :param confidence: 정책 신경망 -> 소프트맥스 확률값
        :return: 현재 손익(portfolio_value / initial_balance - 1)
        """
        # 매수, 매도가 유효하지 않으면 관망
        if not self.validate_action(action):
            action = Agent.ACTION_HOLD

        # 환경에서 현재 가격 얻기
        curr_price = self.environment.get_price()

        # 매수
        if action == Agent.ACTION_BUY:
            # 매수할 단위를 판단
            trading_unit = self.decide_trading_unit(confidence)
            balance = (
                self.balance - curr_price *
                (1 + self.TRADING_CHARGE) * trading_unit
            )
            # 보유 현금이 모자랄 경우 보유 현금으로 매수 가능한 최대 주식 수 계산
            if balance < 0:
                trading_unit = min(
                    int(self.balance / (curr_price * (1 + self.TRADING_CHARGE))),
                    int(self.max_trading_price / curr_price)
                )
            # 수수료를 적용하여 총 매수 금액 산정
            invest_amount = curr_price * (1 + self.TRADING_CHARGE) * trading_unit
            if invest_amount > 0:
                # 평균 매수 단가 갱신 = (기존평균매수단가 * 보유주식수 + 현재가 * 매수수량) / (보유주식수 + 매수수량)
                self.avg_buy_price = (
                    (self.avg_buy_price * self.num_stocks + curr_price * trading_unit)
                    / (self.num_stocks + trading_unit)
                )
                self.balance -= invest_amount  # 보유 현금 갱신 = 잔고 - 매수금액
                self.num_stocks += trading_unit  # 보유 주식 수 갱신
                self.num_buy += 1  # 매수 횟수 증가

        # 매도
        elif action == Agent.ACTION_SELL:
            # 매도할 단위를 판단
            trading_unit = self.decide_trading_unit(confidence)
            # 보유 주식이 모자랄 경우 보유 수량 전량 매도
            trading_unit = min(trading_unit, self.num_stocks)
            # 매도
            invest_amount = curr_price * (
                1 - (self.TRADING_TAX + self.TRADING_CHARGE)) * trading_unit
            if invest_amount > 0:
                # 평균 매수 단가 갱신
                self.avg_buy_price = (
                    (self.avg_buy_price * self.num_stocks - curr_price * trading_unit)
                    / (self.num_stocks - trading_unit)
                    if self.num_stocks > trading_unit else 0    # 남은 수량 없으면 0
                )
                self.num_stocks -= trading_unit  # 보유 주식 수를 갱신
                self.balance += invest_amount  # 보유 현금을 갱신
                self.num_sell += 1  # 매도 횟수 증가

        # 관망
        elif action == Agent.ACTION_HOLD:
            self.num_hold += 1  # 관망 횟수 증가

        # 포트폴리오 가치 갱신
        self.portfolio_value = self.balance + curr_price * self.num_stocks
        self.profitloss = self.portfolio_value / self.initial_balance - 1
        return self.profitloss