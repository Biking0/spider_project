# encoding:utf-8
import random
import json

import requests

from example import settings


def get_port_city():
    res = requests.get(settings.GET_PORT_CITY_URL, timeout=60, verify=False)
    json_content = json.loads(res.text)
    return json_content.get('data')


def strip_item(item):
    for k, v in item.items():
        if isinstance(v, str):
            item[k] = v.strip()
    return item


def keys_to_short(data):
    item = dict()
    item['f'] = data.get('flight_number')
    item['d'] = data.get('dep_time')
    item['a'] = data.get('arr_time')
    item['fc'] = data.get('from_city')
    item['tc'] = data.get('to_city')
    item['da'] = data.get('dep_port')
    item['aa'] = data.get('arr_port')
    item['c'] = data.get('currency')
    item['ap'] = data.get('adult_price')
    item['at'] = data.get('adult_tax')
    item['n'] = data.get('net_fare')
    item['m'] = data.get('max_seats')
    item['cb'] = data.get('cabin')
    item['cr'] = data.get('carrier')
    item['i'] = data.get('is_change')
    item['s'] = data.get('segments')
    item['g'] = data.get('get_time')
    item['info'] = data.get('info')
    return item


# 根据频率选取随机的url
def get_random_url(data_dict):
    start = 0
    prob = data_dict.values()
    rand_num = random.randint(1, sum(prob))
    for k, v in data_dict.items():
        start += v
        if rand_num <= start:
            return k


def parse_data(data):
    p = data.split(':')
    dep_arr = p[0].split('-')
    dep = dep_arr[0]
    arr = dep_arr[1]
    dt = p[1]
    days = p[2]
    return dt, dep, arr, days



