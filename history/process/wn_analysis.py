import time
import sys
from datetime import datetime
from datetime import timedelta
from collections import Counter

import pandas as pd
import numpy as np

from utils import util
from utils.mysql import MySql


# pd.set_option('display.max_columns', None) # 展示所有列，数据过大默认不展示

# for item in util.get_id('WN'):


# item = next(util.get_id('WN'))
def wn_analyst(item, df_all):
    # print(item)
    index = ['depTime', 'addtime', 'flightNumber', 'cabin', 'seats', 'price', 'invalid', 'bId', 'preTime']
    # print(flight_data)
    # index = ['addtime', 'price', 'preTime']
    df = pd.DataFrame(item, columns=index)
    # df.columns = ['add_dt', 'price', 'dt_diff']
    # df.drop(columns=['dep_dt','flight', 'id'], inplace=True)
    df['shift(1)'] = df['price'].shift(1)
    df.fillna(df['price'][0], inplace=True)
    df['price_diff'] = df['price'] - df['shift(1)']
    df['p_d_percent'] = df['price_diff'] * 100 / df['shift(1)']
    # 计算距出发时间多少小时
    df['dt_diff_h'] = df['preTime'] / 60 / 60
    # df.drop(columns=['shift(1)'], inplace=True)
    df.rename(columns={'shift(1)': 'last_price'}, inplace=True)
    df['last_seats'] = df['seats'].shift(1)
    df.fillna(df['seats'][0], inplace=True)
    df['last_cabin'] = df['cabin'].shift(1)
    df.fillna(df['cabin'][0], inplace=True)
    df1 = df.loc[df['price_diff'] != 0]
    df_all = df_all.append(df1, sort=True)
    # print(df_all)
    return df_all


def process(percent=20, price_diff=100, seat_clean=None, num_clean=None):
    # df_all = pd.DataFrame.from_csv('price_diff.csv')
    df_all = pd.read_csv('src/data/price_diff.csv')
    if seat_clean:
        # 取得两次变价座位相等的情况
        df_clean = df_all.loc[df_all['last_seats'] == df_all['seats']].copy()
    else:
        df_clean = df_all.copy()
    # 新想法，获取当天的零点时间戳，减去零点的时间戳进行分析
    df_clean['depTime'] = df_clean['depTime'].astype('int')
    df_clean['that_day'] = df_clean['depTime'] - df_clean['depTime'] % 86400
    df_clean['dt_diff_h'] = (df_clean['that_day'] - df_clean['addtime']) / 60 / 60
    df_clean['dt_diff_h'] = df_clean['dt_diff_h'].astype('int')
    # df2 = df_clean.loc[df_clean['price_diff'] >= 5].copy()
    df_analysis = df_clean.loc[(df_clean['p_d_percent'] >= percent) | (df_clean['price_diff'] >= price_diff)].copy()
    # 聚合相同的时间
    c = Counter()
    for ch in list(df_analysis['dt_diff_h']):
        c[ch] = c[ch] + 1
    # df3 = pd.DataFrame([c])
    # df3.stack().to_csv('bbb.csv')
    df3 = pd.DataFrame.from_dict(c, orient='index', columns=['num'])
    # 倒序显示不同时间的变价数量
    # df3.sort_values('num', ascending=False, inplace=True)
    # 整理变价数量大于50并按顺序排列
    if num_clean:
        df3 = df3.loc[df3['num'] >= num_clean].copy()
    df3 = df3.reindex(list(range(1000)), fill_value=0)
    df3.sort_index(inplace=True)
    file_name = "src/data/percent=%s&price_diff=%s.csv" % (percent, price_diff)
    df3.to_csv(file_name)
    print('生成%s成功' % file_name)


def main():
    index = [
        'depTime', 'addtime', 'flightNumber', 'cabin', 'seats', 'last_cabin',
        'last_seats',  'price', 'last_price', 'invalid', 'bId', 'preTime'
    ]
    df_all = pd.DataFrame(columns=index)
    db = MySql()
    for i in range(-30, 30):
        yd = datetime.now() - timedelta(days=i)
        yd = yd.strftime('%Y%m%d')
        for id in db.get_id('WN', yd):
            item = db.get_series(id, yd)
            try:
                df_all = wn_analyst(item, df_all)
            except:
                import traceback
                traceback.print_exc()
                continue

    df_all.to_csv('src/data/price_diff.csv', encoding='utf_8_sig')


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) == 1:
        print(
            "将要执行获取WN变价代码，若想获取数据分析，请执行：\n"
            "python wn.py percent=20 price_diff=100 =50 seat_clean=1"
            "\npercent:获取升价多少百分比以上\n"
            "price_diff：获取涨价超过多少美元以上\n"
            "num_clean：是否去除每小时小于多少的数据，默认不清除\n"
            "seat_clean：是否排除座位不相同，1为排除，默认不排除\n"
        )
        time.sleep(5)
        print("正在执行WN变价数据获取，预计完成需要3个小时")
        main()
    else:
        percent, price_diff, num_clean, seat_clean = 20, 100, None, None
        for arg in argv[1:]:
            v_a = arg.split('=')
            if 'percent' == v_a[0]:
                percent = v_a[1]
            if 'price_diff' == v_a[0]:
                price_diff = v_a[1]
            if 'num_clean' == v_a[0]:
                num_clean = v_a[1]
            if 'seat_clean' == v_a[0]:
                seat_clean = v_a[1]

        process(percent, price_diff, num_clean, seat_clean)
