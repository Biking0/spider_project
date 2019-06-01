# encoding=utf-8
# aq
# by hyn
# 2019-02-12

import requests, time, json, logging, random
import traceback
from datetime import datetime, timedelta


def is_aq_ok(proxies, timeout=10):
    try:
        url = "http://www.9air.com/aq/GetFlight"
        date = datetime.now() + timedelta(days=10)
        date = date.strftime('%Y-%m-%d')
        querystring = {"ori": "XIY", "dest": "CAN", "traveldate": date, "currency": "CNY"}
        res = requests.request("GET", url, proxies=proxies, params=querystring, timeout=10)
        json_dict = json.loads(res.text)

        if json_dict.get('errorcode') == '9990':
            return False
        return True
    except Exception as e:
        # print(e)
        return False


def _get_proxy():
    proxy = ''
    try:
        li = json.loads(requests.get('http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=be', time).text)
        logging.info('Proxy Num: ' + str(len(li)))
        logging.info(str(li))
        proxy = random.choice(li) or ''
        print(proxy)
    except Exception as e:
        print(e)
        traceback.print_exc()
        logging.info('get proxy error....')
    finally:
        return proxy or ''


if __name__ == '__main__':
    while True:
        ip_port = _get_proxy()
        proxies = {
            'http': 'http://%s' % ip_port,
            # 'https': 'http://%s' % ip_port
        }
        print(is_aq_ok(proxies))
        time.sleep(1)
