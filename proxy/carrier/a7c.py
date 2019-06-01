# encoding=utf-8
# flyadeal,F3
# by hyn
# 2018-12-26

import requests, time, json, logging, random
import traceback


def is_a7c_ok(proxies, timeout=30):
    try:
        url = "https://www.jejuair.net/jejuair/cn/main.do"
        res = requests.get(url, proxies=proxies, timeout=timeout)
        if res.status_code is not 200:
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
            'https': 'http://%s' % ip_port
        }
        print(is_a7c_ok(proxies))
        time.sleep(1)
