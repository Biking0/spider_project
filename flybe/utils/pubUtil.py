#encoding:utf-8
import sys
import json
import time
import logging
from datetime import datetime, timedelta

import requests
from dateutil.tz import tzlocal

sys.path.append('..')  # 测试专用

from flybe_spider import settings


def timezone_is_cst():
    if datetime.now(tzlocal()).tzname() != 'CST':
        print('the timezone is not cst. please config it by this command:')
        print('1. sudo tzselect # Asia -> China -> yes')
        print('2. sudo cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime')
        print('3. date # check it again !')
        sys.exit()


def getProxy():
    try:
        ip = requests.get(settings.HTTPS_IP_URL).text
    except:
        return None
    return 'https://' + ip

def adjustDate(fromDate): #调整日期为今天之后
    from_datetime = datetime.strptime(fromDate, '%Y-%m-%d')
    from_time = from_datetime.timetuple()
    from_stamp = time.mktime(from_time)
    diff = 0
    right_datetime = from_datetime
    while from_stamp < time.time():
        diff += 1
        right_datetime = from_datetime + timedelta(days=diff)
        right_time = right_datetime.timetuple()
        from_stamp = time.mktime(right_time)
    final = right_datetime.strftime('%Y-%m-%d')
    return final

def dateIsInvalid(dt): # 是过去的日期
    dt_time = time.strptime(dt, '%Y-%m-%d')
    dt_stamp = time.mktime(dt_time)
    if dt_stamp < time.time():
        return True
    return False

def analysisData(data):
    p = data.split(':')
    fromTo = p[0].split('-')
    dep = fromTo[0]
    to = fromTo[1]
    dt = datetime.strptime(p[1], '%Y%m%d').strftime('%Y-%m-%d')
    return (dt, dep, to)


def getUrl(carrier,num=1):
    params = {
        'carrier': carrier,
        'num': num,
    }
    try:
        content = requests.get(settings.GET_TASK_URL, params=params, timeout=settings.GET_URL_TIMEOUT).text
        s = requests.session()
        s.keep_alive = False
        data = json.loads(content)
    except:
        return None
    if 'status' not in data or data['status'] != 0:
        return None
    dt = data.get('data')
    return dt

def pushUrl(data):
    datas = {
        'carrier': data['carrier'],
        'als': data['als'],
        'dts': data['dts'],
    }
    try:
        res = requests.post(settings.PUSH_TASK_URL, data=json.dumps(datas), timeout=settings.GET_URL_TIMEOUT)
        s = requests.session()
        s.keep_alive = False
    except:
        logging.info('pushUrl Error...')

def pushData(action, infos):
    data = {
        'action': action,
        'data': infos
    }
    param = {'carrier': infos[0]['carrier']}
    requests.adapters.DEFAULT_RETRIES = 5
    res = requests.post(settings.PUSH_DATA_URL,params=param, data=json.dumps(data), headers={'Connection': 'close'}, timeout=settings.GET_URL_TIMEOUT)
    print('pushData: ' + res.text + ' num: ' + str(len(infos)))
    s = requests.session()
    s.keep_alive = False

def insertLog(carrier, dt, dep, to, name, log_content):
    data = {}
    data['fromDate'] = time.mktime(time.strptime(dt, '%Y-%m-%d'))
    data['fromCity'] = dep
    data['toCity'] = to
    data['carrier'] = carrier
    data['content'] = log_content
    data['nodename'] = name
    datas = {
        'action' : 'add',
        'data': [data],
    }
    param = {'carrier': carrier}
    requests.adapters.DEFAULT_RETRIES = 5
    try:
        res = requests.post(settings.LOG_URL, params=param, data=json.dumps(datas), timeout=settings.GET_URL_TIMEOUT)
    except:
        return

def heartbeat(name, carrier, num, permins, version):
    params = {
        'carrier': carrier,
        'num': num,
        'name': name,
        'permins': permins,
        'version': version,
    }
    try:
        return requests.get(settings.HEARTBEAT_URL, params=params, timeout=settings.GET_URL_TIMEOUT).text
    except:
        return

if __name__ == '__main__':
    print(getUrl('BE', 30))