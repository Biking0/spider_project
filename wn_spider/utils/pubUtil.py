# encoding:utf-8
import sys

sys.path.append('..')  # 测试专用
import settings
import requests, json, os, csv
from datetime import datetime, timedelta
import time, logging, traceback, random

from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header
from dateutil.tz import tzlocal

BASIC_TIME = 0


# 从小池子中获取IP
def get_proxy(carrier):
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
        params = {'carrier': carrier}
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

def push_cookies(cookies, carrier):
    if not len(cookies):
        return
    data = dict(
        cookies=cookies,
        carrier=carrier
    )
    url = settings.ADD_COOKIES_URL
    try:
        res = requests.post(url, data=json.dumps(data), timeout=30)
        logging.info(res.text)
        status = json.loads(res.text).get('status')
        if not status:
            return res.text
    except Exception as e:
        logging.info(e)
        traceback.print_exc()
        time.sleep(3)


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
    except:
        print('Use Windows will report error, do not close temporarily!!!')


def send_email(subject, content, receivers=settings.SPIDER_RECEIVERS):
    message = MIMEText(content, 'html')
    message['From'] = 'robot@lamudatech.com'
    message['Subject'] = Header(subject, 'utf-8')
    index = random.randint(0, len(settings.SENDER) - 1)
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


def dateIsInvalid(dt):  # 是过去的日期
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


def getUrl(carrier, num=1, url=None):
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
        print(content)
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
        res = requests.post(push_data_url, data=json.dumps(data), headers={'Connection': 'close'},
                            timeout=settings.GET_URL_TIMEOUT)
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
        carrier = infos[0].get('carrier')
    params = {'carrier': carrier}
    requests.adapters.DEFAULT_RETRIES = 5
    try:
        res = requests.post(push_data_url, params=params, data=json.dumps(data), headers={'Connection': 'close'}, timeout=settings.GET_URL_TIMEOUT)
        return 'pushData: ' + res.text + ' num: ' + str(len(infos))
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
        'action': 'add',
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
        print(traceback.print_exc())
        return 'heartbeat error'


if __name__ == '__main__':
    # task = {
    #     'arrAirport': 'BHX',
    #     'date': '20180615',
    #     'depAirport': 'VIE',
    # }
    # print(invalidData('invalid', [task], 'http://dx.spider2.jiaoan100.com/br/newairline?carrier=ew', 'lin'))
    # num = 0
    # while True:
    #     print(num)
    #     getUrl('TW')
    #     time.sleep(2)
    #     num += 1
    push_cookies(['haha'], 'wn')
    # heartbeat('hyn-test', '1', '1', '1', '1')
