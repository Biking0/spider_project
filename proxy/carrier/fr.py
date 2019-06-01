# encoding:utf-8
import requests,time,json,logging, traceback, sys
from datetime import datetime, timedelta
import random, os, csv
from random import randint
from urllib import parse
sys.path.append('..')

def get_ports():
    input_file = open(os.path.join('src', 'FR.csv'))
    reader = csv.reader(input_file)
    citys = list(reader)
    input_file.close()
    return citys

CITYS = get_ports()

def is_fr_ok(proxies, timeout_seconds=10):
    return True
    timeout_seconds = timeout_seconds
    _date = (datetime.now() + timedelta(days=randint(3, 10))).strftime('%Y-%m-%d')
    test_url = 'https://desktopapps.ryanair.com/v4/en-ie/availability?'
    dep, arr = random.choice(CITYS)
    params = parse.urlencode(dict(
        ADT=1, CHD=0, DateOut=_date, Destination=arr, FlexDaysOut=2,
        INF=0, IncludeConnectingFlights=True, Origin=dep, RoundTrip=False,
        TEEN=0, ToUs='AGREED', exists=False
    ))
    # print(params)
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Origin': 'https://www.ryanair.com',
        'Referer': 'https://www.ryanair.com/gb/en/booking/home',
        # 'Cookie':'RYANSESSION=WjdorQolAroAAC-PPAcAAAA1',
        'Host': 'desktopapps.ryanair.com',
        'Accept': 'application/json;text/plain,*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    try:
        response = requests.get(test_url + params, proxies=proxies, timeout=timeout_seconds, headers=HEADERS)
        flight = json.loads(response.text)
        if response.status_code == 200 and 'trips' in flight:
            # print(response.text)
            return True
        print(response.text)
        return False
    except Exception as e:
        # traceback.print_exc()
        return False

def _get_proxy():
    proxy=''
    try:
        li = json.loads(requests.get('http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=BE', timeout=30).text)
        logging.info('Proxy Num: ' + str(len(li)))
        logging.info(str(li))
        proxy = random.choice(li) or ''
        print(proxy)
    except:
        traceback.print_exc()
        logging.info('get proxy error....')
    finally:
        return proxy or ''

if __name__ == '__main__':
    # get_ports()
    while True:
        ip_port = _get_proxy()
        proxies = {
            'http': 'http://%s' % ip_port,
            'https': 'https://%s' % ip_port
        }
        # proxies=None
        print(is_fr_ok(proxies))
        time.sleep(5)