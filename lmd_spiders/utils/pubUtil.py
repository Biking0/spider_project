# encoding:utf-8
import os
import csv
import sys
import json
import time
import random
import logging
import requests
import traceback
from datetime import datetime, timedelta

from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header
from dateutil.tz import tzlocal


sys.path.append('..')  # 测试专用
from lmd_spiders import settings


def get_task(carrier, step=1, days=7):
    input_file = open(os.path.join('utils/src', '%s.csv' % carrier.upper()))
    reader = csv.reader(input_file)
    data_list = list(reader)
    input_file.close()

    this_day = datetime.now() + timedelta(days=1)
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
    '''
    判断时区是否是中国上海
    '''
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


def gen_cmd(carrier, argv):
    if len(argv) < 2:
        print('pls input like this:')
        print('python be_spider.py lin 1 ')
        sys.exit()

    num = 1 if len(argv) < 3 else argv[2]  # 爬虫序号

    arg_set = set()  # 生成后面的参数
    arg_big = set()
    if len(argv) > 3:
        for arg in argv[3:]:
            if arg == '1':  # 兼容以前的proxy版本的
                arg_set.add('proxy=1')
            else:
                k, v = arg.split('=')
                if k == 'local':
                    arg_big.add('CLOSESPIDER_TIMEOUT=0')

                if k.isupper():
                    arg_big.add(arg.replace(' ', ''))
                else:
                    arg_set.add(arg.replace(' ', ''))

    arg_str = ''
    if len(arg_set):
        arg_str = ' -a ' + ' -a '.join(arg_set)
    if len(arg_big):
        arg_str += ' -s ' + ' -s '.join(arg_big)

    cmd = 'scrapy crawl %s -a host_name=%s -a num=%s' % (carrier, argv[1], num) + arg_str

    return cmd


def send_email(subject, content, receivers=settings.SPIDER_RECEIVERS):
    message = MIMEText(content, 'html')
    message['From'] = 'robot@lamudatech.com'
    message['Subject'] = Header(subject, 'utf-8')
    index = random.randint(0, len(settings.SENDER)-1)
    try:
        smtp = SMTP_SSL(settings.HOST_SERVER)
        smtp.ehlo(settings.HOST_SERVER)
        smtp.login(settings.SENDER[index], settings.PWD[index])
        smtp.sendmail(settings.SENDER[index], receivers, message.as_string())
        smtp.quit()
        logging.info('success')
    except:
        logging.error(traceback.print_exc())
        time.sleep(5)

def change_to_int(hms):
    h, m, s = hms.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


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
    dt_time = time.strptime(dt + " 23:59:59", '%Y-%m-%d %H:%M:%S')
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


def getUrl(carrier,num=1, url=None):
    params = {
        'carrier': carrier,
        'num': num,
    }
    headers = {
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.9",
        'cache-control': "no-cache",
        'connection': "keep-alive",
        'host': "116.196.116.117",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    }
    try:
        if not url:
            url = settings.GET_TASK_URL
        content = requests.get(url, headers=headers, params=params, timeout=settings.GET_URL_TIMEOUT).text
    except:
        # traceback.print_exc()
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
        res = requests.post(settings.PUSH_TASK_URL, data=json.dumps(datas), timeout=settings.GET_URL_TIMEOUT)
        s = requests.session()
        s.keep_alive = False
    except:
        logging.info('pushUrl Error...')

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
        res = requests.post(push_data_url, data=json.dumps(data), headers={'Connection': 'close'}, timeout=settings.GET_URL_TIMEOUT)
        print('invalidData: ' + res.text + ' num: ' + str(len(infos)))
        return True
    except:
        return False


def addData(action, infos, push_data_url, host_name, carrier=None):
    if not len(infos):
        return True
    data = {
        'action': action,
        'data': infos,
        'name': host_name
    }
    if not carrier:
        carrier = infos[0].get('carrier') or infos[0].get('cr')
    params = {'carrier': carrier}
    requests.adapters.DEFAULT_RETRIES = 5
    try:
        res = requests.post(push_data_url, params=params, data=json.dumps(data), headers={'Connection': 'close'}, timeout=settings.GET_URL_TIMEOUT)
        print('pushData: ' + res.text + ' num: ' + str(len(infos)))
        return True
    except:
        # traceback.print_exc()
        return False

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
    except:
        return 'heartbeat error'

if __name__ == '__main__':
    # task = {
    #     'arrAirport': 'BHX',
    #     'date': '20180615',
    #     'depAirport': 'VIE',
    # }
    # print(invalidData('invalid', [task], 'http://dx.spider2.jiaoan100.com/br/newairline?carrier=ew', 'lin'))
    num = 0
    while True:
        print(num)
        getUrl('TW')
        time.sleep(2)
        num += 1
