# encoding=utf-8
# flyscoot,TR
# by hyn
# 2018-12-25

import requests, time, json, logging, random
import traceback


def is_tr_ok(proxies, timeout=10):
    try:
        get_token_url = "https://prod.open.flyscoot.com/v1/identity/token"
        headers = {
            'User-Agent': 'OS=Android;OSVersion=6.0.1;AppVersion=2.0.2;DeviceModel=XiaomiMI4LTE;',
            'Accept-Language': 'zh_CN',
            'Host': 'prod.open.flyscoot.com',
            'Accept-Encoding': 'gzip',
            'Connection': 'keep-alive',
            'Accept': 'application/json'
        }
        res = requests.post(get_token_url, proxies=proxies, headers=headers, timeout=timeout)
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
        print(is_tr_ok(proxies))
        time.sleep(1)
