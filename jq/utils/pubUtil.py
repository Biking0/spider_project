# encoding:utf-8
import sys
import settings

sys.path.append('..')  # 测试专用
import requests, json, os, csv, random
from datetime import datetime, timedelta
import time, logging, traceback
import settings as db


# 从小池子中获取IP
def jq_get_proxy():
    # num = spider.custom_settings.get('PROXY_TRY_NUM', 10)
    # if spider.isOK:
    #     return self.proxy
    # if self.proxy_count < num and self.proxy != '':
    #     self.proxy_count = self.proxy_count + 1
    #     logging.info('using old proxy:' + self.proxy)
    #     return self.proxy
    #
    # self.proxy_count = 0
    # if self.token_count >= 5:

    #     logging.info('# update token')
    #     self.token_count = 0
    #     self.get_token(spider)
    #     return
    proxy = ''
    try:
        params = {'carrier': 'jq'}
        li = json.loads(requests.get(settings.GET_PROXY_URL, params=params, timeout=settings.GET_URL_TIMEOUT,
                                     verify=False).text)
        logging.info('Proxy Num: ' + str(len(li)))
        logging.info(str(li))
        proxy = random.choice(li).decode('ascii') or ''
        # self.token_count = self.token_count + 1
    except:
        traceback.print_exc()
        logging.info('get proxy error....')
        return
    finally:
        # spider.proxy_flag = False
        return proxy


# 获取本地任务
def get_task(carrier, step=1, days=7):
    input_file = open(os.path.join('utils/', '%s.csv' % carrier.upper()), 'rU')
    reader = csv.reader(input_file)
    data_list = list(reader)
    input_file.close()

    this_day = datetime.now() + timedelta(days=3)
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


def addData(action, infos, push_data_url, host_name, carrier=None):
    if not len(infos):
        return True
    data = {
        'action': action,
        'data': infos,
        'name': host_name
    }
    if not carrier:
        carrier = infos[0].get('cr')
    params = {'carrier': carrier}
    requests.adapters.DEFAULT_RETRIES = 5
    try:
        res = requests.post(push_data_url, params=params, data=json.dumps(data), headers={'Connection': 'close'},
                            timeout=settings.GET_URL_TIMEOUT)
        print('pushData: ' + res.text + ' num: ' + str(len(infos)))
        return True
    except:
        # traceback.print_exc()
        return False


def invalidData(action, infos, push_data_url, host_name):
    if not len(infos):
        return True
    data = {
        'action': action,
        'data': infos,
        'name': host_name
    }
    requests.adapters.DEFAULT_RETRIES = 5
    try:
        res = requests.post(push_data_url, data=json.dumps(data), headers={'Connection': 'close'},
                            timeout=settings.GET_URL_TIMEOUT)
        print('invalidData: ' + res.text + ' num: ' + str(len(infos)))
        return True
    except:
        return False


def adjustDate(fromDate):  # 调整日期为今天之后
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


def dateIsInvalid(dt):
    dt_time = time.strptime(dt, '%Y-%m-%d')
    dt_stamp = time.mktime(dt_time)
    if dt_stamp < time.time():
        return True
    return False


def getUrl(carrier, num=1):
    params = {
        'carrier': carrier,
        'num': num,
    }
    try:
        content = requests.get(db.GET_TASK_URL, params=params, timeout=db.GET_URL_TIMEOUT).text
        s = requests.session()
        s.keep_alive = False
    except:
        return None
    data = json.loads(content)
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
        res = requests.post(db.PUSH_TASK_URL, data=json.dumps(datas), timeout=db.GET_URL_TIMEOUT)
        s = requests.session()
        s.keep_alive = False
    except:
        pass


def pushData(carrier, action, infos):
    data = {
        'action': action,
        'data': infos
    }
    param = {'carrier': carrier}
    requests.adapters.DEFAULT_RETRIES = 5
    try:
        res = requests.post(db.PUSH_DATA_URL, params=param, data=json.dumps(data), headers={'Connection': 'close'},
                            timeout=db.GET_URL_TIMEOUT)
        print('pushData: ' + res.text + ' num: ' + str(len(infos)) + ' ' + action)
    except:
        time.sleep(0.01)
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
        'action': 'add',
        'data': [data],
    }
    param = {'carrier': carrier}
    requests.adapters.DEFAULT_RETRIES = 5
    try:
        requests.post(db.LOG_URL, params=param, data=json.dumps(datas), timeout=db.GET_URL_TIMEOUT)
    except:
        return


def heartbeat(name, carrier, num, permins, version=1):
    params = {
        'carrier': carrier,
        'num': num,
        'name': name,
        'permins': permins or 0,
        'version': version
    }
    try:
        return requests.get(db.HEARTBEAT_URL, params=params, timeout=db.GET_URL_TIMEOUT).text
    except:
        return


if __name__ == '__main__':
    infos = {
        'date': '20180324',
        'fromCity': 'MIL',
        'toCity': 'BCN',
    }
    pushData('VY', 'invalid', [infos])
