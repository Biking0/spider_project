
import json
import time
import logging
from datetime import datetime, timedelta

import requests

import settings


def get_id(carrier, ts=None, tp=None):
    if not ts:
        ts = yesterday()
    url = settings.GET_ID
    params = dict(
        carrier=carrier,
        ts=ts,
    )
    if tp:
        params['tp'] = tp
    page = 0
    while True:
        params['page'] = page
        while True:
            try:
                res = requests.get(url, params=params, timeout=30)
                data = json.loads(res.text).get('data')
                time.sleep(1)
                break
            except Exception as e:
                print(e)
                time.sleep(10)
                continue
        for item in data:
            yield keys_to_long(item)
        if len(data) < 500:
            break
        page += 1


def get_history(flight, id):
    url = settings.GET_HISTORY
    params = dict(
        flight=flight,
        id=id
    )
    while True:
        try:
            res = requests.get(url, params=params, timeout=30)
            if res.status_code == 500:
                return
            data = json.loads(res.text)
            break
        except Exception as e:
            print(flight, id)
            print(e)
            time.sleep(5)
            continue
    series_list = data.get('series')
    if not series_list or not len(series_list):
        return
    dep_time = data.get('deptime')
    series = []
    try:
        series_list.sort()
        # if dep_time > time.time():
        #     last_item = series_list[-1].copy()
        #     last_item[0] = time.time()
        #     series_list.append(last_item)
        for one in series_list:
            item = dict(
                depTime=dep_time,
                addtime=one[0],
                cabin=one[1],
                seats=one[2],
                price=one[3],
                invalid=one[4],
                bId=id,
                flightNumber=flight,
                preTime=dep_time - one[0]
            )
            series.append(item)
        return series
    except Exception as e:
        print(e)
        print(url, params)


def get_dates(st_date, en_date):
    st_dt = datetime.strptime(st_date, '%Y%m%d')
    en_dt = datetime.strptime(en_date, '%Y%m%d')
    flag = st_dt
    while flag <= en_dt:
        yield flag.strftime('%Y%m%d')
        flag += timedelta(days=1)


def keys_to_long(item):
    ans = dict()
    for short, long in settings.KEY_MAP.items():
        if short in item:
            ans[long] = item[short]
    return ans


def yesterday():
    yd = datetime.now() - timedelta(days=1)
    return yd.strftime('%Y%m%d')


def validate(ids):
    if not ids or not len(ids):
        return
    url = settings.VALIDATE_URL
    data = dict(
        operate=1,
        ids=ids,
    )
    while True:
        try:
            res = requests.post(url, data=json.dumps(data), timeout=30)
            if res.status_code == 200:
                logging.info('validate success: ' + res.text)
                return
        except Exception as e:
            print(e)
        time.sleep(5)


if __name__ == '__main__':
    # for id in get_id('F3', '20181231'):
    #     print(id)
    # print(get_history('none', 426024279))
    validate([419015847, 418031222])


