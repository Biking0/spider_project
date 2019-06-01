# encoding: utf-8
import sys
import json
import os
import csv
from datetime import datetime, timedelta
import requests
import random
from dateutil.tz import tzlocal
from example import settings


def get_task(carrier, step=1, days=7):
    input_file = open(os.path.join('utils/src', '%s.csv' % carrier.upper()), 'rU')
    reader = csv.reader(input_file)
    data_list = list(reader)
    input_file.close()

    this_day = datetime.now() + timedelta(days=7)
    # 打乱顺序
    random.shuffle(data_list)

    for i in range(0, days, step):
        _date = this_day + timedelta(days=i)
        _dt = _date.strftime('%Y%m%d')
        for data in data_list:
            if not data or not len(data):
                continue
            print(['%s-%s:%s:%s' % (data[0], data[1], _dt, step)])
            yield ['%s-%s:%s:%s' % (data[0], data[1], _dt, step)]


def timezone_is_cst():
    """
    判断时区是否是中国上海
    """
    try:
        if datetime.now(tzlocal()).tzname() != 'CST':
            print('the timezone is not cst. please config it by this command:')
            print('1. sudo tzselect # Asia -> China -> yes')
            print('2. sudo cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime')
            print('3. date # check it again !')
            sys.exit()
    except Exception as e:
        print(e)
        print('Use Windows will report error, do not close temporarily!!!')


def heartbeat(name, carrier, num, permins, version=1):
    params = {
        'carrier': carrier,
        'num': num,
        'name': name,
        'permins': permins or 0,
        'version': version,
    }
    try:
        return requests.get(settings.HEARTBEAT_URL, params=params, timeout=settings.GET_URL_TIMEOUT).text
    except Exception as e:
        print(e)
        return 'heartbeat error'


def get_url(carrier, num=1):
    params = {
        'carrier': carrier,
        'num': num,
    }
    try:
        url = settings.GET_TASK_URL
        content = requests.get(url, params=params, timeout=settings.GET_URL_TIMEOUT).text
    except Exception as e:
        # traceback.print_exc()
        print(e)
        return None
    data = json.loads(content)
    if 'status' not in data or data['status'] != 0:
        return None
    dt = data.get('data')
    return dt


def operate_data(action, infos, push_data_url, host_name, carrier=None):
    """
    :param action: includes： add and invalid
    :param infos:  data
    :param push_data_url: url
    :param host_name:
    :param carrier:
    :return:
    """
    if not len(infos):
        return True
    data = {
        'action': action,
        'data': infos,
        'name': host_name
    }
    if not carrier:
        carrier = infos[0].get('carrier')
    params = {'carrier': carrier}
    try:
        res = requests.post(push_data_url, params=params, data=json.dumps(data), headers={'Connection': 'close'},
                            timeout=settings.GET_URL_TIMEOUT)
        print('pushData: ' + res.text + ' num: ' + str(len(infos)))
        return True
    except Exception as e:
        print(e)
        # traceback.print_exc()
        return False
