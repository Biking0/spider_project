# -*- coding: utf-8 -*-
import json
import time
import random
import requests
import logging
import traceback
from datetime import datetime,timedelta


def is_wn_ok(proxies,timeout_seconds=10):
    try:
        url = 'https://www.southwest.com/'
        res = requests.get(url, timeout=timeout_seconds, proxies=proxies)
        # print(res.text)
        # print(res.status_code)
        if res.status_code == 200:
            return True
        return False
    except:
        return False


def _get_proxy():
    proxy=''
    try:
        url = 'http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=pc'
        li = json.loads(requests.get(url, timeout=60).text)
        logging.info('Proxy Num:' + str(len(li)))
        logging.info(str(li))
        proxy = random.choice(li) or ''

        print(proxy)
    except:
        traceback.print_exc()
        logging.info('get proxy error....')
    finally:
        return proxy or ''


if __name__ == '__main__':
    while True:
        ip_port = _get_proxy()
        proxies = {
            'http': 'http://%s' % ip_port,
            'https': 'https://%s' % ip_port
        }
        print(is_wn_ok(proxies))
        time.sleep(5)
