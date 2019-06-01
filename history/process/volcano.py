# encoding: utf-8
import os
import csv
from datetime import datetime

import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt

from utils import util


class Volcano:

    volcano_time = 24 * 60 * 60
    stand_rate = 0.8
    validate_rate = 0.01

    def __init__(self, carrier):
        self.need_validate = []
        self.carrier = carrier

    def record(self):
        util.validate([i[0] for i in self.need_validate])
        output_file = open(os.path.join('src/validate', self.carrier + '.csv'), 'a')
        writer = csv.writer(output_file)
        writer.writerows(self.need_validate)
        output_file.close()
        self.need_validate = []

    def run(self, series):
        if not series or not len(series):
            return
        if self.can_validate(series):
            id = series[0]['bId']
            fn = series[0]['flightNumber']
            dt = datetime.fromtimestamp(series[0]['depTime']).strftime('%Y-%m-%d')
            dt_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(id, fn, dt)
            self.need_validate.append([id, fn, dt, dt_now])

    def volcano(self, series):
        """
        判断是不是那种长时间不存在， 后又突然出现的数据， 然后又迅速没有的数据
        判断标准： 从座位数为0到座位数不为0相差时间超过一天， 且在一天内又恢复为0的数据
        :param series:
        :return:
        """
        df = pd.DataFrame(series, columns=['seats', 'addtime'])
        df = df.sort_values(by='addtime')
        df['prediff'] = df.diff()['addtime']  # 获取当前行的addtime与上一行的addtime差值
        seats = df.seats
        for i in range(1, len(seats) - 1):
            if seats[i] and not seats[i - 1] and df.prediff[i] > self.volcano_time:
                if not seats[i + 1] and df.prediff[i + 1] < self.volcano_time:
                    # self.draw('addtime', 'seats', df)
                    return True
        return False

    def can_validate(self, series):
        """
        判断是不是那种长时间不存在， 后又突然出现的数据， 然后又迅速没有的数据
        判断标准： 最后一天出现座位数为零的时间占比
        :param series:
        :return:
        """
        df = pd.DataFrame(series, columns=['seats', 'addtime'])
        df.sort_values(by='addtime', inplace=True)
        df['nextdiff'] = abs(df.diff(-1)['addtime'])  # 获取当前行的addtime与下一行的addtime差值
        df = df.sort_values(by=['addtime'], ascending=[False])
        df.fillna(0, inplace=True)
        df.reset_index(inplace=True)
        seats = df.seats
        diff = df.nextdiff
        if not seats[0]:
            return False
        sum_all, sum_0 = 0, 0
        for i in range(len(seats)):
            # 最近的一个小时， 如果存在seats为0的

            last_time = self.volcano_time - sum_all
            sum_all += diff[i]
            if sum_all >= self.volcano_time:
                sum_all = self.volcano_time
                if 0 >= seats[i]:
                    sum_0 += last_time
                break
            if 0 >= seats[i]:
                sum_0 += diff[i]

        rate = sum_0 / sum_all
        if rate <= self.validate_rate:
            print(rate, series[0]['bId'])
            # self.draw('addtime', 'seats', df)
            return True
        return False

    def judge_top(self, seats, diff):
        sum_seats = 0
        for i in len(seats):
            pass
        if seats[0] <= 0:
            return False

    def copy_pre(self, df_old):
        df_new = df_old.copy()
        df_new.addtime = df_new['addtime'].shift(1)
        df_new['addtime'] = df_new['addtime'] - 1
        df = df_old.append(df_new, ignore_index=True)
        df.dropna(axis=0, subset=['addtime'], inplace=True)
        df.fillna(0, inplace=True)
        df.sort_values(by='addtime', inplace=True)
        return df

    def draw(self, x, y, df):
        df = self.copy_pre(df)
        sns.lineplot(x=x, y=y, data=df)
        plt.show()


if __name__ == '__main__':
    from utils import util
    vol = Volcano('TW')
    series = util.get_history('ZE705', 420025728)
    vol.run(series)