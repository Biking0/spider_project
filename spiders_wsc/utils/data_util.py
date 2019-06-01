# encoding:utf-8
import random
import json

import requests

from spiders_wsc import settings


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
    keys_map = settings.KEYS_MAP
    for long, short in keys_map.items():
        if long in data and None is not data.get(long):
            item[short] = data[long]
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

#获取最低票价




