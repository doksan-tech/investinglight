# 종목 데이터에서의 에이전트 위치와 데이터 반환

class Environment:
    PRICE_IDX = 4  # 종가의 위치

    def __init__(self, chart_data=None):
        """
        chart_data: pandas DataFrame(날짜, 시가, 고가, 저가, 종가, 거래량)
        :param chart_data:
        """
        self.chart_data = chart_data    # 종목 데이터
        self.observation = None         # 현재 관측치 -> (날짜, 시가, 고가, 저가, 종가, 거래량)
        self.idx = -1                   # 데이터에서의 현재 위치

    def reset(self):
        """
        idx, observation 초기화 -> 데이터의 처음으로 돌아감
        :return: 없음
        """
        self.observation = None
        self.idx = -1

    def observe(self):
        """
        idx를 다음 위치(다음 날)로 이동시키고 observation 업데이트
        더 이상 제공할 데이터가 없을 때는 None 반환
        :return: observation or None
        """

        # 인덱스의 다음 위치보다 데이터의 전체길이가 크다면 가져올 데이터가 있다는 의미
        if len(self.chart_data) > self.idx + 1:
            self.idx += 1
            self.observation = self.chart_data.iloc[self.idx]
            return self.observation
        return None

    def get_price(self):
        """
        현재 observation의 종가 반환. 종가의 위치는 5번째 = 인덱스 4
        :return: 종가 or None
        """
        if self.observation is not None:
            return self.observation[self.PRICE_IDX]
        return None

