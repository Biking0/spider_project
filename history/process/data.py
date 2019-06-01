# encoding: utf-8
import json

import pandas as pd

from utils import util

"""
在入库前对数据的处理， （皆是过去的数据）
"""


class Handle:

    def run_active(self, series):
        """
        在这里可以添加对历史数据的其它处理， 流式的
        :param item: 数据历史数据
        :return:
        """
        add_up = self.add_up(series)
        ret = dict(addup=add_up)
        return ret

    def run_base(self, item):
        """
        这里可以添加对原数据的处理
        :param item: 原数据
        :return:
        """
        return item

    def add_up(self, item_list):
        index = ['date', 'cabin', 'seat', 'price', 'tag']
        item = [[i['addtime'], i['cabin'], i['seats'], i['price'], i['invalid']] for i in item_list]
        df = pd.DataFrame(item, columns=index)
        # pd.set_option('display.max_columns', None) # 展示所有列，数据过大默认不展示
        data_max = df.max()
        data_min = df.min()
        # 获取价格表
        price_list = list(set(df['price']))
        price_list.sort()

        # 添加价格变动与时间差
        df.sort_values('date', inplace=True)  # 以日期进行排序
        df['shift(1)'] = df['date'].shift(1)
        df['date_diff'] = df['date'] - df['shift(1)']
        df['shift(1)'] = df['price'].shift(1)
        df['price_diff'] = df['price'] - df['shift(1)']
        df['p_d_percent'] = df['price_diff'] * 100 / df['shift(1)']  # 计算涨价跌百分比，按原价格计算
        df.drop(['shift(1)'], axis=1, inplace=True)  # 删除算差价用的位移行
        df['date_diff'] = item_list[0].get('depTime') - df['date']  # 计算距出发时间
        # df['p_d_p_our'] = '[' + df['price_diff'].map(str) + ',' + df['date_diff'].map(str) + ',' + df['p_d_percent'].map(str) + ']'
        df = df.round(decimals=2)  # 所有数字保留两位小数
        df.fillna(0, inplace=True)  # 去除数据中的nan数字，防止错误
        df1 = df.loc[df['price_diff'] != 0.00]  # 赋予一个价差不为0的df
        price_date_percent_diff = [[x, y, z] for x, y, z in
                                   zip(df1['price_diff'], df1['date_diff'], df1['p_d_percent'])]
        Price_change_diff = df1['date_diff'].min()
        price_diff_list = list(set(df1['price_diff']))  # 相邻变动价格差
        ret_data = {
            'seat_min': data_min.get('seat'),
            'seat_max': data_max.get('seat'),
            'price_min': data_min.get('price'),
            'price_max': data_max.get('price'),
            'price_list': price_list,
            'average_price': float(df['price'].mean()),  # 价格平均值
            'price_change_diff': float(Price_change_diff),  # 发生变价的最小时间差
            'price_diff_list': price_diff_list,
            'price_date_percent_diff': price_date_percent_diff,
            'dep_time': item_list[0].get('deptime'),
            'flight': item_list[0].get('flight'),
            'price_times': len(price_list)
        }
        return json.dumps(ret_data)


if __name__ == '__main__':
    # series =[{'depTime': 1552380300, 'addtime': 1549942241, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2438059}, {'depTime': 1552380300, 'addtime': 1549954655, 'cabin': 'T', 'seats': 120, 'price': 734.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2425645}, {'depTime': 1552380300, 'addtime': 1549954710, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2425590}, {'depTime': 1552380300, 'addtime': 1549957082, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2423218}, {'depTime': 1552380300, 'addtime': 1549957082, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2423218}, {'depTime': 1552380300, 'addtime': 1549957082, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2423218}, {'depTime': 1552380300, 'addtime': 1549957093, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2423207}, {'depTime': 1552380300, 'addtime': 1549957162, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2423138}, {'depTime': 1552380300, 'addtime': 1549957162, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2423138}, {'depTime': 1552380300, 'addtime': 1549957163, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2423137}, {'depTime': 1552380300, 'addtime': 1549957237, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2423063}, {'depTime': 1552380300, 'addtime': 1549957237, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2423063}, {'depTime': 1552380300, 'addtime': 1549957365, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422935}, {'depTime': 1552380300, 'addtime': 1549957420, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422880}, {'depTime': 1552380300, 'addtime': 1549957439, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422861}, {'depTime': 1552380300, 'addtime': 1549957472, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422828}, {'depTime': 1552380300, 'addtime': 1549957472, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422828}, {'depTime': 1552380300, 'addtime': 1549957504, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422796}, {'depTime': 1552380300, 'addtime': 1549957504, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422796}, {'depTime': 1552380300, 'addtime': 1549957569, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422731}, {'depTime': 1552380300, 'addtime': 1549957569, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422731}, {'depTime': 1552380300, 'addtime': 1549957598, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422702}, {'depTime': 1552380300, 'addtime': 1549957599, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422701}, {'depTime': 1552380300, 'addtime': 1549957607, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422693}, {'depTime': 1552380300, 'addtime': 1549957671, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422629}, {'depTime': 1552380300, 'addtime': 1549957671, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422629}, {'depTime': 1552380300, 'addtime': 1549957707, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422593}, {'depTime': 1552380300, 'addtime': 1549957747, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422553}, {'depTime': 1552380300, 'addtime': 1549957802, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422498}, {'depTime': 1552380300, 'addtime': 1549957802, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422498}, {'depTime': 1552380300, 'addtime': 1549957802, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422498}, {'depTime': 1552380300, 'addtime': 1549957803, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422497}, {'depTime': 1552380300, 'addtime': 1549957841, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422459}, {'depTime': 1552380300, 'addtime': 1549957970, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422330}, {'depTime': 1552380300, 'addtime': 1549957970, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422330}, {'depTime': 1552380300, 'addtime': 1549957970, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422330}, {'depTime': 1552380300, 'addtime': 1549958006, 'cabin': 'T', 'seats': 120, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2422294}, {'depTime': 1552380300, 'addtime': 1549958319, 'cabin': 'T', 'seats': 117, 'price': 634.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2421981}, {'depTime': 1552380300, 'addtime': 1549961337, 'cabin': 'T', 'seats': 120, 'price': 734.34, 'invalid': 2, 'bId': 436027812, 'flightNumber': 'none', 'preTime': 2418963}]
    series = util.get_history('ZE214', 426024279)
    hand = Handle()
    # print(hand.volcano(series))
    print(hand.volcano_by_pro(series))
